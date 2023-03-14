def SQL_query():
    sql_statement = """
        SET NOCOUNT ON;
        DECLARE @today DATE = GETDATE()
        DECLARE @fiscalYear INT = CASE WHEN MONTH(@today) < 7 THEN YEAR(@today) ELSE YEAR(@today) + 1 END

        DECLARE @termCodes TABLE (semester VARCHAR(20), term VARCHAR(20))
        INSERT INTO @termCodes VALUES
        ('S1', 'Q1'), ('S1', 'Q2'), ('S1', 'S1'), ('S1', 'YR'),
        ('S2', 'Q3'), ('S2', 'Q4'), ('S2', 'S2'), ('S2', 'YR')


        DECLARE @currentSchedule TABLE (
            CourseTitle VARCHAR(500),
            StudentId VARCHAR(800),
            SchoolNumber VARCHAR(300),
            TeacherId VARCHAR(800),
            BeginningPeriod VARCHAR(200),
            CourseNumber VARCHAR(120),
            DepartmentCode VARCHAR(300),
            Grade VARCHAR(200))
        INSERT INTO @currentSchedule (
            CourseTitle,
            StudentId,
            SchoolNumber,
            TeacherId,
            BeginningPeriod,
            CourseNumber,
            DepartmentCode,
            Grade)
        SELECT CourseTitle, StudentId, SchoolNumber, TeacherId, BeginningPeriod, CourseNumber, DepartmentCode, Grade
        FROM Datawarehouse.dbo.Student_CurrentSchedule
        WHERE AddDropTag = 'C'
            AND CourseNumber NOT LIKE 'LUN%'
            -- commented out requirement below, had to do to get TMS groups to populate
            --might have to add back in to grab CP English courses
            --AND CourseTitle NOT LIKE '% S2'
            AND TermCode in (SELECT term FROM @termCodes WHERE semester = 'S2')
            AND Grade BETWEEN '03' AND '12'

        ;WITH ADMINS AS
        ( -- 0 secs
            SELECT
                Employee.empdistid
               ,Employee.FirstName AS [First Name]
               ,Employee.LastName AS [Last Name]
               ,Employee.EMailAddress AS [Email Address]
               ,Employee.BusinessPhone AS [Phone Number]
               ,Employee.PrimaryWorkLocation
               ,CASE WHEN JobCode.LongName LIKE '%PRIN%' THEN 1 ELSE 0 END AS Principal
               ,CASE WHEN Employee.empdistid = '01019317' THEN 1 ELSE 0 END AS Dummy -- Andres' empdistid is a placeholder for the teacher.
               ,JobCode.ShortName
            FROM
                Datawarehouse.dbo.Employees AS Employee
                INNER JOIN Datawarehouse.dbo.Employee_Positions AS Position ON Employee.EmployeeID = Position.EmployeeID
                    AND Position.PrimaryPosition = 1
                    AND Position.FiscalYear = @fiscalYear
                    AND (Position.enddate IS NULL OR GETDATE() BETWEEN Position.effectivedate AND Position.enddate)
                INNER JOIN Datawarehouse.dbo.JobCodes AS JobCode ON Position.JobCode = JobCode.Code
            WHERE
                Employee.empdistid IN (
                     '01008011' -- Ryan Reynolds.      JC 58
                    ,'01017315' -- Amanda Moore
                    ,'01003725' -- Brad Goudeau.       JC 103
                    ,'01016684' -- Heather Contreras   JC 10022
                    ,'01015624' -- Maricela Mota
                    ,'01020088' -- Laurie Hulin        JC 10022
                    ,'01008030' -- Mike Rich           JC 10012
                    ,'01019335' -- Sara Noguchi        JC 100
                    ,'01020904' -- Anne Bonilla
                    ,'01020133' -- Will Nelson
                    ,'01022189' -- Rey Anaya
                    ,'01023041' -- Jesus Salas-Rodriguez
                    ,'01019317' -- Reserving spot for the actual teacher, Andres Fernandez.
                    )
                OR JobCode.LongName LIKE '%PRIN%' -- Principals
        ),
        Employee AS
        ( -- 0 secs
            SELECT empdistid, LastName, FirstName, MiddleName, EMailAddress
            FROM Datawarehouse.dbo.Employees
            WHERE EMailAddress IS NOT NULL
        ),
        QUERY AS
        (
            SELECT DISTINCT
                RIGHT(sc.SchoolYear, 4) + ' - '
                    + Employee.LastName + ', '
                    + Employee.FirstName +  ' - '
                    + cs.BeginningPeriod
                    + CASE WHEN Admins.Dummy = 1 THEN '' ELSE ' - ' + Admins.ShortName + '_' + Admins.[Last Name] END
                    AS group_name
               ,'50' + CSIS_District + CSIS_School AS school_natural_id
               ,RIGHT(sc.SchoolYear, 4) AS school_year
               ,'ALL' AS subject_code
               ,Student.CsisIdNumber as student_ssid
               ,CASE WHEN Admins.Dummy = 1 THEN Employee.EMailAddress ELSE Admins.[Email Address] END as group_user_login
               ,cs.Grade
               ,cs.CourseNumber
               ,Student.InstructionalSettingCode
               ,cs.DepartmentCode
               ,cs.SchoolNumber
            FROM
                @currentSchedule cs
                INNER JOIN Datawarehouse.dbo.Student AS Student ON Student.StudentId = cs.StudentId AND CsisIdNumber IS NOT NULL
                INNER JOIN Datawarehouse.dbo.School ON School.SchoolNum = cs.SchoolNumber
                        AND School.CSIS_District IS NOT NULL AND School.CSIS_District IS NOT NULL
                INNER JOIN Employee ON Employee.empdistid = cs.TeacherId
                INNER JOIN ADMINS AS Admins ON Admins.PrimaryWorkLocation = CAST(cs.SchoolNumber AS INT)
                        OR Admins.Principal = 0
                INNER JOIN Datawarehouse.dbo.School_Calendar sc ON @today BETWEEN sc.StartDate AND sc.EndDateContiguous
                        --AND sc.Term = 'YR'
                        AND sc.Term = 'S2'
        )

        SELECT
            group_name
           ,school_natural_id
           ,school_year
           ,subject_code
           ,student_ssid
           ,group_user_login
        FROM QUERY
        WHERE
            -- can remove the SchoolNumber <> '027' when rosters for Tuolumne K-6 need to be updated.
            -- will have to add back in when grabbing rosters for TMS
            (Grade BETWEEN '03' AND '06' AND CourseNumber LIKE 'HR%')
            OR
            --SchoolNumber max changed to 37 to include Tuolumne Middle School which is school number 37, orginally looked at schools 32-25
            (InstructionalSettingCode NOT IN ('91', '30', '90') AND DepartmentCode IN ('ENG', 'MAT', 'SCI', 'SPE') AND (SchoolNumber BETWEEN '032' AND '037' OR SchoolNumber >= '040'))
            --, 'ENG JH','MAT JH','SCI JH', 'SPE JH'
        ORDER BY school_natural_id, group_name, student_ssid
            """
    return sql_statement