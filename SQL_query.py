def SQL_query():
    sql_statement = """
    SELECT            
        DISTINCT
        stu.STUDENT_NUMBER as 'Student Id'
        ,YEAR(cc.[DATEENROLLED]) + CASE WHEN MONTH(cc.[DATELEFT]) > 7 THEN 1 ELSE 0 END AS 'YEAR'            
        ,stu.GRADE_LEVEL
        ,stu.TEAM
        ,cc.SCHOOLID as 'School ID'
        ,cc3.COURSE1
        ,cc3.COURSE2
        ,tea.LAST_NAME
        ,tea.FIRST_NAME
    FROM            
        AttunityHS.ps.CC
        INNER JOIN AttunityHS.ps.STUDENTS stu
            ON stu.ID = cc.STUDENTID
        INNER JOIN AttunityHS.ps.COURSES cou
            ON cou.COURSE_NUMBER = cc.COURSE_NUMBER
        INNER JOIN AttunityHS.ps.TEACHERS tea
        ON tea.ID = cc.TEACHERID
        INNER JOIN (
                SELECT
        cc.TEACHERID
        ,cc.COURSE1
        ,cc.COURSE1NUM
        ,cc.COURSE2
        ,cc.COURSE2NUM
    FROM
        (SELECT                    
            cc.TeacherID
            ,cou.COURSE_NAME AS COURSE1
            ,cou.COURSE_NUMBER AS COURSE1NUM
            ,LAG(cou.COURSE_NAME, 1) OVER(PARTITION BY cc.TeacherID, ABS(cc.TERMID) ORDER BY cc.TEACHERID  ASC) AS COURSE2
            ,LAG(cou.COURSE_NUMBER, 1) OVER(PARTITION BY cc.TeacherID, ABS(cc.TERMID) ORDER BY cc.TEACHERID  ASC) AS COURSE2NUM
            ,cc.SCHOOLID
        FROM
            AttunityHS.ps.CC cc
            INNER JOIN AttunityHS.ps.Courses cou ON cc.COURSE_NUMBER = cou.COURSE_NUMBER
        WHERE 1=1
            AND LEFT(ABS(cc.TERMID), 2) = (YEAR(GETDATE()) - 1990) - CASE WHEN MONTH(GETDATE()) > 7 THEN 0 ELSE 1 END
            AND cou.COURSE_Name LIKE '%home room%'
            AND cou.Course_Name NOT LIKE '%virtual%'
            AND cou.Course_Name NOT LIKE '%dual language%'
            AND cou.COURSE_NAME NOT LIKE '%RISE%'
            AND cou.COURSE_NAME NOT LIKE '%SPECIAL%'
        GROUP BY                    
            cc.TeacherID
            ,cou.COURSE_NAME
            ,cou.COURSE_NUMBER
            ,cc.TERMID
            ,cc.SCHOOLID
        ) cc
    WHERE cc.COURSE2 IS NOT NULL
        AND cc.COURSE1NUM <> cc.COURSE2NUM
                ) cc3
            ON cc3.TEACHERID = cc.TEACHERID
    WHERE 1=1
        AND cc3.COURSE2NUM <> cc3.COURSE1NUM
        AND LEFT(ABS(cc.TERMID), 2) = (YEAR(GETDATE()) - 1990) - CASE WHEN MONTH(GETDATE()) > 7 THEN 0 ELSE 1 END
        AND cou.COURSE_Name LIKE '%home room%'
        AND cou.Course_Name NOT LIKE '%virtual%'
        AND cou.Course_Name NOT LIKE '%dual language%'
        AND cou.COURSE_NAME NOT LIKE '%RISE%'
        AND cou.COURSE_NAME NOT LIKE '%SPECIAL%'
    ORDER BY
        stu.STUDENT_NUMBER
            """
    return sql_statement
