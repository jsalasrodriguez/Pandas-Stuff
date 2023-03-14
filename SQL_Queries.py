def query_byschool():
    sql_statement = """		
        -- Ds & Fs @ for School By Year	
    DECLARE @SchoolID as int = 33
    select	
        CONCAT(t.YEARID - 10, '-', t.YEARID - 9) AS Year
        ,COUNT(DISTINCT g.STUDENTID) AS Students
        ,g.STORECODE
        ,COUNT(*) AS Grades
        ,SUM(CASE WHEN LEFT(g.GRADE, 1) = 'D' THEN 1 ELSE 0 END) AS Ds
        ,SUM(CASE WHEN LEFT(g.GRADE, 1) = 'F' THEN 1 ELSE 0 END) AS Fs
        ,SUM(CASE WHEN LEFT(g.GRADE, 1) IN ('A', 'B', 'C') THEN 1 ELSE 0 END) AS 'A-Cs'
        ,SUM(CASE WHEN LEFT(g.GRADE, 1) IN ('A', 'B', 'C', 'D', 'F') THEN 0 ELSE 1 END) AS 'Other'
    from		
        ( 	
        SELECT g.TERMID, g.GRADE, g.STUDENTID, g.STORECODE, SCHOOLID FROM AttunityK8_July10th2020.ps.STOREDGRADES g 
        where g.STORECODE = 'S1' and TERMID < 2700 AND g.SCHOOLID = @SchoolID
        UNION
        SELECT g.TERMID, g.GRADE, g.STUDENTID, g.STORECODE, SCHOOLID FROM AttunityHS.ps.STOREDGRADES g 
        WHERE g.STORECODE = 'S1' and TERMID >= 2000 and (TERMID >= 2700 or g.SCHOOLID >= 40) AND g.SCHOOLID = '33'
        ) g	
        inner join AttunityHS.ps.TERMS t ON t.ID = g.TERMID AND t.SCHOOLID = 43 -- Use Modesto High as default Terms (all schools are the same)
    where g.STORECODE = 'S1'	
    and g.SCHOOLID = '33'
    group by CONCAT(t.YEARID - 10, '-', t.YEARID - 9), g.STORECODE, YEARID	
    order by Year DESC, g.STORECODE DESC	
          """
    return sql_statement


def query_district():
    sql_statement = """
    -- Ds & Fs @ By District	-- Mark Rate		
    select		
          CONCAT(t.YEARID - 10, '-', t.YEARID - 9) AS Year	
        , COUNT(DISTINCT g.STUDENTID) AS Students	
        , g.STORECODE	
        , COUNT(*) AS Grades	
        --, max(g.studentid) AS MaxStu	
        --, max(termid) as MaxTermID	
        , SUM(CASE WHEN LEFT(g.GRADE, 1) = 'D' THEN 1 ELSE 0 END) AS Ds	
        , SUM(CASE WHEN LEFT(g.GRADE, 1) = 'F' THEN 1 ELSE 0 END) AS Fs	
        , SUM(CASE WHEN LEFT(g.GRADE, 1) IN ('A', 'B', 'C') THEN 1 ELSE 0 END) AS 'A-Cs'	
        , SUM(CASE WHEN LEFT(g.GRADE, 1) IN ('A', 'B', 'C', 'D', 'F') THEN 0 ELSE 1 END) AS 'Other'	
    from		
        ( 	
            SELECT g.TERMID, g.GRADE, g.STUDENTID, g.STORECODE FROM AttunityK8_July10th2020.ps.STOREDGRADES g
            where g.STORECODE = 'S1' and TERMID <= 2600
            UNION
            SELECT g.TERMID, g.GRADE, g.STUDENTID, g.STORECODE FROM AttunityHS.ps.STOREDGRADES g 
            WHERE g.STORECODE = 'S1' and TERMID >= 2000 and (TERMID >= 2700 or g.SCHOOLID >= 40)
        ) g	
        inner join AttunityHS.ps.TERMS t ON t.ID = g.TERMID AND t.SCHOOLID = 43 -- Use Modesto High as default Terms (all schools are the same)	
    where 1=1		
    group by CONCAT(t.YEARID - 10, '-', t.YEARID - 9), g.STORECODE, YEARID		
    order by Year DESC, g.STORECODE DESC		
    """
    return sql_statement


def query_StudentRateDisct():
    sql_statement = """
        -- Ds & Fs @ for District By Year Use this for Student Rate 		
        ;with studentsWithDF AS (			
        select		
              g.TERMID	
            --, COUNT(DISTINCT g.STUDENTID) AS Students	
            , g.STORECODE	
            , g.STUDENTID	
            , MAX(CASE WHEN LEFT(g.GRADE, 1) = 'F' THEN 1 ELSE 0 END) AS Fs	
            , MAX(CASE WHEN LEFT(g.GRADE, 1) IN ('D', 'F') THEN 1 ELSE 0 END) AS DsFs	
        from		
            ( 	
                SELECT g.TERMID, g.GRADE, g.STUDENTID, g.STORECODE FROM AttunityK8_July10th2020.ps.STOREDGRADES g 
                where g.STORECODE = 'S1' and TERMID < 2700
                UNION
                SELECT g.TERMID, g.GRADE, g.STUDENTID, g.STORECODE FROM AttunityHS.ps.STOREDGRADES g 
                WHERE g.STORECODE = 'S1' and TERMID >= 2000 and (TERMID >= 2700 or g.SCHOOLID >= 40)
            ) g	
        where 1=1		
        group by g.STORECODE, TERMID, STUDENTID		
    )			
    select			
          CONCAT(t.YEARID - 10, '-', t.YEARID - 9) AS Year		
        , COUNT(DISTINCT s.STUDENTID) AS Students		
        , t.ABBREVIATION AS StoreCode		
        , SUM(Fs) AS StudentsWithF		
        , SUM(DsFs) AS StudentsWithDsFs		
    from			
        studentsWithDF s		
        inner join AttunityHS.ps.TERMS t ON t.YEARID = LEFT(s.TERMID, 2) AND t.ABBREVIATION = s.STORECODE AND t.SCHOOLID = 43 -- Use Modesto High as default Terms (all schools are the same)		
    where 1=1			
    group by CONCAT(t.YEARID - 10, '-', t.YEARID - 9), YEARID, ABBREVIATION			
    order by Year DESC			
    """
    return sql_statement


def query_StudentRateSchool():
    sql_statement = """
        -- Ds & Fs @ La Loma By Year Use this for Student Rate
        DECLARE @SchoolID as int = 33 		
        ;with studentsWithDF AS (			
        select		
              g.TERMID	
            --, COUNT(DISTINCT g.STUDENTID) AS Students	
            , g.STORECODE	
            , g.STUDENTID	
            , MAX(CASE WHEN LEFT(g.GRADE, 1) = 'F' THEN 1 ELSE 0 END) AS Fs	
            , MAX(CASE WHEN LEFT(g.GRADE, 1) IN ('D', 'F') THEN 1 ELSE 0 END) AS DsFs	
        from		
            ( 	
                SELECT g.TERMID, g.GRADE, g.STUDENTID, g.STORECODE FROM AttunityK8_July10th2020.ps.STOREDGRADES g 
                where g.STORECODE = 'S1' and TERMID < 2700 AND g.SCHOOLID = '33' -- Change this for School
                UNION
                SELECT g.TERMID, g.GRADE, g.STUDENTID, g.STORECODE FROM AttunityHS.ps.STOREDGRADES g 
                WHERE g.STORECODE = 'S1' and TERMID >= 2000 and (TERMID >= 2700 or g.SCHOOLID >= 40) AND g.SCHOOLID = @SchoolID
            ) g	
        where 1=1		
        group by g.STORECODE, TERMID, STUDENTID		
    )			
    select			
          CONCAT(t.YEARID - 10, '-', t.YEARID - 9) AS Year		
        , COUNT(DISTINCT s.STUDENTID) AS Students		
        , t.ABBREVIATION AS StoreCode		
        , SUM(Fs) AS StudentsWithF		
        , SUM(DsFs) AS StudentsWithDsFs		
    from			
        studentsWithDF s		
        inner join AttunityHS.ps.TERMS t ON t.YEARID = LEFT(s.TERMID, 2) 
        AND t.ABBREVIATION = s.STORECODE AND t.SCHOOLID = 43 -- Use Modesto High as default Terms (all schools are the same)		
    where 1=1			
    group by CONCAT(t.YEARID - 10, '-', t.YEARID - 9), YEARID, ABBREVIATION			
    order by Year DESC			
    """
    return sql_statement
