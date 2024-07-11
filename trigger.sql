DELIMITER $$
CREATE TRIGGER discordUsers_insert_trigger
AFTER INSERT
    ON discordUsers.registered
    FOR EACH ROW
BEGIN
    INSERT INTO RODB.login (
        userid,
        user_pass,
        email,
        sex,
        group_id,
        state,
        unban_time,
        expiration_time,
        logincount,
        last_ip,
        birthdate,
        character_slots,
        pincode,
        pincode_change
    )
    VALUES (
        NEW.Username,
        NEW.Password,
        NEW.Email,
        'M',
        '0',
        '0',
        '0',
        '0',
        '0',
        '',
        NULL,
        '0',
        '',
        '0'
    );
END$$
DELIMITER ;
