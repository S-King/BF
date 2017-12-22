DELIMITER //
 
CREATE PROCEDURE `SyncDailyPrices` ()
BEGIN
    DECLARE a, b, c INT;
    DECLARE cur1 CURSOR FOR SELECT * FROM test t LEFT JOIN btcclosingprice btc ON t.MYSQL_DateFormat = btc.date WHERE t.MYSQL_DateFormat BETWEEN  '2017-1-1 00:00:00' AND NOW( )  AND btc.USD IS NULL;

 
 
    DECLARE CONTINUE HANDLER FOR NOT FOUND SET b = 1;
    OPEN cur1;
 
    SET b = 0;
    SET c = 0;
    
    WHILE b = 0 DO
        FETCH cur1 INTO a;
        IF b = 0 THEN
            SET c = c + a;
    END IF;  
    END WHILE;
 
    CLOSE cur1;
    SET param1 = c;
 
END //