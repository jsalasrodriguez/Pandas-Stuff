def student(x, y, z, t, d, s):
    variable = x
    school_year = y
    sasi = z
    psasi = t
    dsasi = d
    pseniors = s
    sql_statement = f""" 
    DECLARE @CurrentSchoolYear varchar(7) = '{school_year}' -- CCYY-YY
    DECLARE @DesiredSasiSchoolyear varchar(4) = '{sasi}'
    DECLARE @PriorSasiSchoolYear varchar(4) = '{psasi}'
    DECLARE @DesiredSchoolYear varchar(4) = '{dsasi}' -- CCYY
    DECLARE @IncludePriorYearSeniors bit = {pseniors} -- 1 for Summer/Fall submissions & 0 for Spring submissions
    DECLARE @DesiredSchoolNumber varchar(3) = '{variable}'


    --SELECT *
    --FROM (

    SELECT -- ISNULL(s.Graduated_SchoolId, s.SasiSchoolNum) AS SasiSchoolNum, sch.ShortName,

        --sch.ShortName,

          CAST(LEFT(sch.CollegeBoard_School, 6) AS numeric) AS 'AMERICAN TESTING PROGRAM CODE'
        , LEFT(s.StudentId, 30) AS 'STUDENT ID'
        , LEFT(ISNULL(s.CsisIdNumber, ''), 10) AS 'CA STATE STUDENT ID'
        , LEFT(s.FirstName, 35) AS 'FIRST NAME'
        , LEFT(s.LastName, 50) AS 'LAST NAME'
        , LEFT(ISNULL(s.ResidenceAddress, ''), 55) AS 'ADDRESS'
        , LEFT(ISNULL(s.ResidenceCity, ''), 35) AS 'CITY'
        , LEFT(ISNULL(s.ResidenceState, ''), 2) AS 'STATE'
        , LEFT(REPLACE(ISNULL(s.ResidenceZipCode, ''),'-',''), 9) AS 'ZIP'
        , ISNULL(FORMAT(CAST(s.BirthDate AS DATE), 'yyyyMMdd'), '') AS 'DOB'
        , LEFT(s.Gender, 1) AS 'GENDER'
        , LEFT(CASE en.Grade WHEN '13' THEN '12' ELSE en.Grade END, 2) AS 'GRADE LEVEL'
        , LEFT(CASE WHEN s.EthnicityCode BETWEEN '100' AND '700' THEN s.EthnicityCode
            WHEN s.EthnicityCode = '900' THEN 'Not Specified'
            WHEN s.EthnicityCode = 'TWO' THEN 'Multiple'
            ELSE '' END, 50) AS 'LOCAL ETHNICITY'
        , LEFT(ISNULL(CASE WHEN s.GraduationDate IS NOT NULL THEN CONCAT(YEAR(s.GraduationDate), RIGHT(CONCAT('00', MONTH(s.GraduationDate)), 2)) ELSE gy.ExpectedGradYear + '05' END, ''), 6) AS 'GRAD DATE' -- CCYYMM
        , '' AS 'RANK' -- Our good Rank data (ex. TOP 10%) doesn't fit their numeric expectation.
        , LEFT(ISNULL(CASE s.FreeLunchCode WHEN 'DirCert' THEN 'Free' WHEN 'Free' THEN 'Free' WHEN 'DirCertR' THEN 'Reduced' WHEN 'Reduced' THEN 'Reduced' ELSE '' END, ''), 7) AS 'MEAL STATUS TYPE' -- Free OR Reduced
        , CASE WHEN
                        --en.SasiYear = @PriorSasiSchoolYear
                        s.Grade IN ('13')
                        THEN 'Y' ELSE 'N' END AS 'PREVIOUS YEAR SENIOR'
    FROM --Datawarehouse_July1st2022.dbo.Student s
    Datawarehouse.dbo.Student s
    INNER JOIN (
            SELECT DISTINCT   en.StudentId
                            , en.Grade
                            , en.SasiYear
            FROM Datawarehouse.dbo.Student_Enrollment en
            WHERE (en.SasiYear = @DesiredSasiSchoolYear OR (@includePriorYearSeniors = 1 AND en.SasiYear = @PriorSasiSchoolYear AND en.Grade IN ('12', '13')))
            AND en.SchoolAttn = @DesiredSchoolNumber
            AND en.DaysEnrolled > 0
    ) en ON en.StudentId = s.StudentId
    LEFT JOIN Datawarehouse.dbo.School sch ON sch.SasiSchoolNum = CASE WHEN s.SasiSchoolNum = '999' THEN s.Graduated_SchoolId ELSE s.SasiSchoolNum END
    LEFT JOIN MCS.dbo.GraduationYears gy ON gy.Grade = CASE WHEN en.Grade = '13' THEN '12' ELSE en.Grade END
    WHERE CASE WHEN s.SasiSchoolNum = '999' THEN s.Graduated_SchoolId ELSE s.SasiSchoolNum END = @DesiredSchoolNumber
    AND ISNULL(s.CsisIdNumber, '') <> ''
    --) a
    --WHERE ISNULL(a.[STUDENT ID], '') = '' OR ISNULL(a.[CA STATE STUDENT ID], '') = ''

    ORDER BY s.LastName, s.FirstName, s.StudentId
    """
    return sql_statement


def test_scores(x, y, z, t, d, s):
    variable = x
    school_year = y
    sasi = z
    psasi = t
    dsasi = d
    pseniors = s
    sql_statement = f""" 
    DECLARE @Today AS date = GETDATE()
    DECLARE @CurrentSchoolYear varchar(7) = '{school_year}' -- CCYY-YY
    DECLARE @DesiredSasiSchoolyear varchar(4) = '{sasi}'
    DECLARE @PriorSasiSchoolYear varchar(4) = '{psasi}'
    DECLARE @DesiredSchoolYear varchar(4) = '{dsasi}' -- CCYY
    DECLARE @MinSchoolYear varchar(4) = '2016' -- Should be no more than 7 year max window.
    DECLARE @MaxSchoolYear varchar(4) = '2022' -- Should be no more than 7 year max window.
    DECLARE @MinClassStartDate date = '8/1/2016' -- Used for current schedule instead of course history.
    DECLARE @IncludePriorYearSeniors bit = {pseniors} -- 0 for Spring submissions & 1 for Summer/Fall submissions
    DECLARE @DesiredSchoolNumber varchar(3) = '{variable}'
    DECLARE @StateSchoolCode varchar(15) = (SELECT TOP 1 sch.CSIS_School FROM MCS.dbo.school sch WHERE sch.SchoolNum = @DesiredSchoolNumber) 

    ;WITH Students AS (
        SELECT DISTINCT s.StudentId
        FROM --Datawarehouse_July2nd2020.dbo.Student s
        Datawarehouse.dbo.Student s
        INNER JOIN (
            SELECT DISTINCT en.StudentId
            FROM Datawarehouse.dbo.Student_Enrollment en
            WHERE (en.SasiYear = @DesiredSasiSchoolYear
                OR (@IncludePriorYearSeniors = 1 AND en.SasiYear = @PriorSasiSchoolYear AND en.Grade IN ('12', '13')))
            AND en.SchoolAttn = @DesiredSchoolNumber
            AND en.DaysEnrolled > 0
        ) en ON en.StudentId = s.StudentId
        WHERE ISNULL(s.CsisIdNumber, '') <> ''
    )

    SELECT
            s.StudentId AS 'STUDENT ID'
          , @StateSchoolCode AS 'AMERICAN TESTING PROGRAM CODE'
          , 'AP'  AS 'TEST TYPE'
          , FORMAT(ap.TestDate,'yyyyMM') AS 'TEST DATE'
          , apex.ExamName  AS 'SUBTEST NAME'
          , ap.ExamScore AS 'TEST SCORE'
    FROM 
        Students s
            INNER JOIN MCS.dbo.APTestScores AS ap ON s.StudentId = ap.StudentId
            INNER JOIN MCS.dbo.APExamCodes AS apex ON ap.ExamCode = apex.ExamCode
    WHERE 
        ap.ExamScore IS NOT NULL

    UNION 
        SELECT
            s.StudentId AS 'STUDENT ID'
          , @StateSchoolCode AS 'AMERICAN TESTING PROGRAM CODE'
          , 'ACT'  AS 'TEST TYPE'
          , CONCAT('20', act.TestYear, act.TestMonth) AS 'TEST DATE'
          , 'COMPOSITE' AS 'SUBTEST NAME'
          ,  act.Comp AS 'TEST SCORE'
        FROM 
            Students s
            INNER JOIN Datawarehouse.dbo.ACTTestScores act ON s.StudentId = act.StudentId

    --UNION
    --	SELECT
    --		s.StudentId AS 'STUDENT ID'
    --	  , @StateSchoolCode AS 'AMERICAN TESTING PROGRAM CODE'
    --	  , 'SAT'  AS 'TEST TYPE'
    --	  , CONCAT('20', sat.TestYear, sat.TestMonth) AS 'TEST DATE'
    --	  , 'COMPOSITE' AS 'SUBTEST NAME'
    --	  ,  sat.[SAT2 Test Score Total] AS 'TEST SCORE'
    --	FROM 
    --		Students s
    --		INNER JOIN Studentdata.dbo.SAT_Subject_Scores sat ON s.StudentId = sat.[High School Student ID]
        --WHERE




    ORDER BY
        s.StudentId, [TEST TYPE]

    """
    return sql_statement


def student_transcript(x, y, z, t, d, s):
    variable = x
    school_year = y
    sasi = z
    psasi = t
    dsasi = d
    pseniors = s
    if pseniors == 1:
        wip = 0
    else:
        wip = 1
    sql_statement = f""" 
    DECLARE @Today AS date = GETDATE()
    DECLARE @CurrentSchoolYear varchar(7) = '{school_year}' -- CCYY-YY -- Used to fill in blank Course History School Year values.
    DECLARE @DesiredSasiSchoolyear varchar(4) = '{sasi}'
    DECLARE @PriorSasiSchoolYear varchar(4) = '{psasi}'
    DECLARE @DesiredSchoolYear varchar(4) = '{dsasi}' -- CCYY
    DECLARE @MinSchoolYear varchar(4) = '2016' -- Should be no more than 7 year max window.
    DECLARE @MaxSchoolYear varchar(4) = '2022' -- Should be no more than 7 year max window.
    DECLARE @MinClassStartDate date = '8/1/2016' -- Used for current schedule instead of course history.
    DECLARE @MaxClassStartDate date = '6/30/2023' -- Used for current schedule instead of course history.
    DECLARE @IncludePriorYearSeniors bit = {pseniors}  -- 1 for Summer/Fall submissions & 0 for Spring submissions
    DECLARE @IncludeWIP bit = {wip}  -- 0 for Fall submissions and 1 for Spring submissions
    DECLARE @DesiredSchoolNumber varchar(3) = '{variable}'

    ;WITH Students AS (
        SELECT DISTINCT s.StudentId, en.Grade, en.SasiYear, en.School AS SasiSchoolNum, s.Graduated_SchoolId, s.CsisIdNumber, s.LastName, s.FirstName
        FROM Datawarehouse.dbo.Student s
        INNER JOIN (
            SELECT DISTINCT en.StudentId, en.Grade, en.SasiYear, en.SchoolAttn AS School
            FROM Datawarehouse.dbo.Student_Enrollment en
            WHERE (en.SasiYear = @DesiredSasiSchoolYear OR (@IncludePriorYearSeniors = 1 AND en.SasiYear = @PriorSasiSchoolYear AND en.Grade IN ('12', '13')))
            AND en.SchoolAttn = @DesiredSchoolNumber
            AND en.DaysEnrolled > 0
        ) en ON en.StudentId = s.StudentId
        WHERE ISNULL(s.CsisIdNumber, '') <> ''
    )

    SELECT
          LEFT(ISNULL(s.StudentId, s2.StudentId), 30) AS 'STUDENT ID'
        , LEFT(CASE WHEN COALESCE(ch.Grade, s.Grade, s2.Grade) = '13' THEN '12' ELSE COALESCE(ch.Grade, s.Grade, s2.Grade) END, 2) AS 'GRADE LEVEL'
        , LEFT(COALESCE(csSch.Name, ch.SchoolAttendedDesc, 'Unknown'), 100) AS 'SCHOOL ATTENDED' -- Blank school name not allowed.
        , LEFT(COALESCE(csSch.CollegeBoard_School, chSch.CollegeBoard_School, ''), 6) AS 'AMERICAN TESTING PROGRAM CODE' -- OPTIONAL
        , LEFT(CASE WHEN csSch.CollegeBoard_School IS NOT NULL THEN CONCAT('50', csSch.CSIS_District, csSch.CSIS_School)
            WHEN chSch.CollegeBoard_School IS NOT NULL THEN CONCAT('50', chSch.CSIS_District, chSch.CSIS_School)
            ELSE '' END, 14) AS 'CDS CODE' -- OPTIONAL
        , LEFT(CASE WHEN ch.SchoolYear IS NULL THEN @CurrentSchoolYear ELSE CAST(ch.SchoolYear AS varchar) + '-' + RIGHT(CAST(ch.SchoolYear + 1 AS varchar), 2) END, 7) AS 'SCHOOL YEAR' -- CCYY-YY
        , LEFT(ISNULL(FORMAT(ISNULL(cs.StartDate, cal.StartDate), 'yyyyMM'), ''), 6) AS 'COURSE START DATE' -- OPTIONAL -- CCYYMM
        , LEFT(ISNULL(FORMAT(ISNULL(cs.EndDate, cal.EndDate), 'yyyyMM'), ''), 6) AS 'COURSE END DATE' -- OPTIONAL -- CCYYMM
    --	, LEFT(CASE WHEN ISNULL(ch.StoreCode, cs.TermCode) = 'S3' THEN CASE WHEN ISNULL(ch.CourseTitle, cs.CourseTitle) LIKE '%S2' THEN 'SS2' ELSE 'SS1' END ELSE ISNULL(ch.StoreCode, cs.TermCode) END, 4) AS 'TERM'
        , LEFT(CASE WHEN ISNULL(ch.StoreCode, cs.TermCode) = 'S3' THEN CASE WHEN ISNULL(ch.CourseTitle, cs.CourseTitle) LIKE '%S2' THEN 'SS2' ELSE 'SS1' END WHEN LEFT(ISNULL(ch.StoreCode, cs.TermCode),1) IN ('D', 'Y') THEN 'F' ELSE ISNULL(ch.StoreCode, cs.TermCode) END, 4) AS 'TERM'
        , LEFT(CASE WHEN sec.PSExpression LIKE '%B%' OR sec.PSExpression LIKE '%C%' THEN 'Y' ELSE 'N' END, 1) AS 'BLOCK SCHEDULE' -- Y/N
        , LEFT(CASE WHEN ch.StudentId IS NULL AND (cs.EndDate IS NULL OR cs.EndDate > @Today) THEN 'Y' ELSE 'N' END, 1) AS 'WORK IN PROGRESS' -- Y/N
        , LEFT(COALESCE(ch.CourseNumber, cs.CourseNumber, CONCAT('NON-MCS ', COALESCE(ch.Department, ch.SubjectArea1Desc, 'Uncategorized'))), 25) AS 'LOCAL COURSE ID' -- Seems like Fall let us submit blank, but Spring will not.
        , LEFT(COALESCE(ch.CourseTitle, cs.CourseTitle, ''), 50) AS 'LOCAL COURSE NAME'
        , LEFT(COALESCE(ch.CreditAttempted, cm.CreditValue, ''), 6) AS 'CREDITS ATMPT' -- ##.### (precision optional)
        , LEFT(ISNULL(ch.CreditEarned, '0.0'), 6) AS 'CREDIT EARNED' -- ##.### (precision optional) 0.0 for in-progress courses
        , REPLACE(LEFT(CASE WHEN ch.StudentId IS NULL AND (cs.EndDate IS NULL OR cs.EndDate > @Today) THEN 'WIP' WHEN ISNUMERIC(ch.Mark) = 1 THEN 'NM' WHEN ch.Mark = 'N/A' THEN 'NM' ELSE ISNULL(ch.Mark, 'NM') END, 3), ' ', '') AS 'COURSE GRADE'
        , LEFT(CASE WHEN LEFT(ISNULL(ch.StoreCode, cs.TermCode), 1) IN ('D', 'Y') THEN 'F' ELSE LEFT(ISNULL(ch.StoreCode, cs.TermCode), 1) END, 2) AS 'CALENDAR TYPE' -- We want LEFT 1, but 2 are allowed.
    FROM --Datawarehouse_July1st2022.dbo.Student s
        --Datawarehouse.dbo.Student s
        Students s
        LEFT JOIN Datawarehouse.dbo.Student_CourseHistory_All ch ON ch.StudentID = s.StudentId AND ch.HS = 1
                AND (ch.SectionId IS NULL OR ch.IsFinalGrade = 1)
        -- The following JOIN can be LEFT if only history is desired; needs to be FULL OUTER if current/next semester desired as well!
        FULL JOIN Datawarehouse.dbo.Student_CurrentSchedule_All cs ON cs.StudentId = s.StudentId AND ch.SectionId = cs.SectionID AND ch.HS = cs.HS
        LEFT JOIN Students s2 ON s2.StudentId = cs.StudentId AND ch.StudentID IS NULL
        LEFT JOIN Datawarehouse.dbo.Section sec ON sec.SectionID = cs.SectionId
        LEFT JOIN Datawarehouse.dbo.CourseMaster cm ON cm.COURSE = ISNULL(sec.CourseNumber, ch.CourseNumber)
        LEFT JOIN Datawarehouse.dbo.School csSch ON csSch.SchoolNum = cs.SchoolNumber
        LEFT JOIN Datawarehouse.dbo.School chSch ON chSch.SasiSchoolNum = ch.SchoolAttended
        LEFT JOIN Datawarehouse.dbo.School_Calendar cal ON cal.PSTermID = ISNULL(ch.TermId, sec.TermId) AND cal.Term = ISNULL(ch.Term, sec.TermCode)
    WHERE
        (s.StudentId IS NOT NULL OR s2.StudentId IS NOT NULL)
        AND CASE WHEN ISNULL(s.SasiSchoolNum, s2.SasiSchoolNum) = '999' THEN ISNULL(s.Graduated_SchoolId, s2.Graduated_SchoolId)
            ELSE ISNULL(s.SasiSchoolNum, s2.SasiSchoolNum) END = @DesiredSchoolNumber
        AND (ch.RepeatFlag IS NULL OR ch.RepeatFlag = '') -- Allow NULL since current courses may not have any course history grades yet.
        --AND (ch.SectionId IS NULL OR ch.IsFinalGrade = 1)
        AND (cs.CourseNumber IS NULL OR LEFT(cs.CourseNumber, 3) NOT IN ('LUN', 'NON'))
        AND (cs.AddDropTag IS NULL OR cs.AddDropTag = 'C')
        AND (ch.Grade IS NULL OR ch.Grade BETWEEN '09' AND '13')
        AND (cm.COURSE IS NULL OR LEFT(cm.COURSE, 3) <> 'UNS')
        AND (ch.SchoolYear IS NULL OR ch.SchoolYear BETWEEN @MinSchoolYear AND @MaxSchoolYear)
        AND (cs.StartDate IS NULL OR cs.StartDate BETWEEN @MinClassStartDate AND @MaxClassStartDate)
        AND (cs.HS IS NULL OR cs.HS = 1)
        AND (ch.StudentID IS NOT NULL OR cs.StudentId IS NOT NULL)
        AND (ISNULL(s2.CsisIdNumber, '') <> '' OR ISNULL(s.CSISIdNumber, '') <> '') -- Records must have a State Student ID.
        AND (ch.StudentId IS NOT NULL OR @IncludeWIP = 1)
    ORDER BY ISNULL(s.LastName, s2.LastName), ISNULL(s.FirstName, s2.FirstName), ISNULL(s.StudentId, s2.StudentId), [SCHOOL YEAR], [Term], cs.BeginningPeriod
    """
    return sql_statement


def program_participation(x, y, z, t, d, s):
    variable = x
    school_year = y
    sasi = z
    psasi = t
    dsasi = d
    pseniors = s
    sql_statement = f""" 
        /*
        NOTE:
        This query only returns one record per student (current school / graduated school).
        The upload allows a record for every student-school-attended combo.
        The combo version is more work than we have time for for the 2019-20 Spring upload.
        This Program Participation portion was not uploaded at all for our first upload (2019-20 Fall).
        Gathering the combo data would require matching EL record dates to school enrollment dates,
            as well as matching special program or instructional setting dates for to school enrollmenet dates for special ed.
            Additional difficulty: our programs are combinations of EL Status and SpecialEd status, making the aforementioned extra complex.

            Trying to solve the above with this new query.
    */

    DECLARE @CurrentSchoolYear varchar(7) = '{school_year}' -- CCYY-YY
    DECLARE @DesiredSasiSchoolyear varchar(4) = '{sasi}'
    DECLARE @PriorSasiSchoolYear varchar(4) = '{psasi}'
    DECLARE @DesiredSchoolYear varchar(4) = '{dsasi}' -- CCYY
    DECLARE @MinSchoolYear varchar(4) = '2016' -- Should be no more than 7 year max window.
    DECLARE @MaxSchoolYear varchar(4) = '2022' -- Should be no more than 7 year max window.
    DECLARE @MinSchoolYearYYYY varchar(4) = '1617' -- Should be no more than 7 year max window.
    DECLARE @MaxSchoolYearYYYY varchar(4) = '2223' -- Should be no more than 7 year max window.
    DECLARE @IncludePriorYearSeniors bit = {pseniors} -- 0 for Spring submissions & 1 for Summer/Fall submissions
    DECLARE @DesiredSchoolNumber varchar(3) = '{variable}'

    ;WITH el AS (
        SELECT tbd.StudentId, 'TBD' AS ELStatus, tbd.id AS Row_id, tbd.TBDStartDate AS StatusStartDate, tbd.TBDEndDate AS StatusEndDate
        FROM Datawarehouse.dbo.Student s
        LEFT JOIN MCS.dbo.Assessment_Detail tbd ON s.StudentId = tbd.StudentID
        WHERE s.StudentStatus IS NULL AND tbd.TBDStartDate IS NOT NULL
        UNION
        SELECT eo.StudentId, 'EO', eo.id AS EO_id, eo.EOStartDate, eo.EOEndDate
        FROM Datawarehouse.dbo.Student s
        LEFT JOIN MCS.dbo.Assessment_Detail eo ON s.StudentId = eo.StudentID
        WHERE s.StudentStatus IS NULL AND eo.EOStartDate IS NOT NULL
        UNION
        SELECT el.StudentId, 'IFEP', el.id AS el_id, el.IFEPStartDate, el.IFEPEndDate
        FROM Datawarehouse.dbo.Student s
        LEFT JOIN MCS.dbo.Assessment_Detail el ON s.StudentId = el.StudentID
        WHERE s.StudentStatus IS NULL AND el.IFEPStartDate IS NOT NULL
        UNION
        SELECT el.StudentId, 'EL', el.id AS el_id, el.elStartDate, el.elEndDate
        FROM Datawarehouse.dbo.Student s
        LEFT JOIN MCS.dbo.Assessment_Detail el ON s.StudentId = el.StudentID
        WHERE s.StudentStatus IS NULL AND el.ELStartDate IS NOT NULL
        UNION
        SELECT el.StudentId, 'RFEP', el.id AS EO_id, el.RFEPStartDate, el.RFEPEndDate
        FROM Datawarehouse.dbo.Student s
        LEFT JOIN MCS.dbo.Assessment_Detail el ON s.StudentId = el.StudentID
        WHERE s.StudentStatus IS NULL AND el.RFEPStartDate IS NOT NULL
    )

    SELECT DISTINCT
          LEFT(s.StudentId, 30) AS 'STUDENT ID'
        -- ISNULL(s.Graduated_SchoolId, s.SasiSchoolNum) AS SasiSchoolNum, sch.ShortName,
        , CAST(LEFT(sch.CollegeBoard_School, 6) AS numeric) AS 'AMERICAN TESTING PROGRAM CODE'
        , CONCAT(ISNULL(s.EnglishProficiencyLevelCode, 'TBD')
            , ' - ', CASE WHEN ISNULL(s.DisabilityCode, '') = '' THEN 'NonSpecialEd' ELSE 'SpecialEd' END
            ) AS 'PROGRAM NAME'
        , 'O' AS 'PROGRAM IDENTIFIER' -- Options: R = Regular; M = Magnate; S = Small Learning Community; O = Other
    FROM
        Datawarehouse.dbo.Student s
        INNER JOIN (
            SELECT DISTINCT en.StudentId
            FROM Datawarehouse.dbo.Student_Enrollment en
            WHERE (en.SasiYear = @DesiredSasiSchoolYear
                OR (@IncludePriorYearSeniors = 1 AND en.SasiYear = @PriorSasiSchoolYear AND en.Grade IN ('12', '13')))
            AND en.SchoolAttn = @DesiredSchoolNumber
            AND en.DaysEnrolled > 0
        ) stuLimiter ON stuLimiter.StudentId = s.StudentId
        LEFT JOIN (
            -- Can only have one record per student-school combo.
            SELECT DISTINCT en.StudentId, en.SchoolAttn, en.EffDate, en.EndDate
            FROM Datawarehouse.dbo.Student_Enrollment en
            WHERE en.SasiYear BETWEEN @MinSchoolYearYYYY AND @MaxSchoolYearYYYY
                AND en.DaysEnrolled > 0
                AND en.Grade BETWEEN '09' AND '13'
                AND en.SchoolAttn = @DesiredSchoolNumber
        ) en ON en.StudentId = s.StudentId
        LEFT JOIN Datawarehouse.dbo.School sch ON sch.SchoolNum = en.SchoolAttn
        LEFT JOIN el ON el.StudentID = en.StudentId
            AND (el.StatusStartDate > en.EffDate OR el.StatusEndDate < en.EndDate)
            AND ((el.StatusEndDate IS NULL OR el.StatusEndDate > en.EffDate) AND el.StatusStartDate < en.EndDate)
    WHERE
        CASE WHEN s.SasiSchoolNum = '999' THEN s.Graduated_SchoolId ELSE s.SasiSchoolNum END = @DesiredSchoolNumber
        AND en.SchoolAttn <> '999'
    ORDER BY 'STUDENT ID', 'AMERICAN TESTING PROGRAM CODE'

    """
    return sql_statement
