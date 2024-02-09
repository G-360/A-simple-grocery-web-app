
CREATE TRIGGER Update_Product_Name
AFTER UPDATE ON Products
FOR EACH ROW
BEGIN
	UPDATE Featured
	SET Product_Name = NEW.Product_Name
	WHERE Featured.Product_ID = OLD.ID;
	UPDATE Cart
	SET Product_Name = NEW.Product_Name
	WHERE Featured.Product_ID = OLD.ID;
END;