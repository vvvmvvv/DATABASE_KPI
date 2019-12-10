CREATE OR REPLACE FUNCTION process_club_audit() RETURNS TRIGGER AS $club_audit$
    BEGIN
        IF (TG_OP = 'DELETE') THEN
            INSERT INTO clubs_audit
            SELECT nextval('audit_id_seq'), 'D'::char, now(), user, OLD.club_id;
            RETURN OLD;
        ELSIF (TG_OP = 'UPDATE') THEN
            INSERT INTO clubs_audit
            SELECT nextval('audit_id_seq'), 'U'::char, now(), user, NEW.club_id;
            RETURN NEW;
        ELSIF (TG_OP = 'INSERT') THEN
            INSERT INTO clubs_audit
            SELECT nextval('audit_id_seq'), 'I'::char, now(), user, NEW.club_id;
            RETURN NEW;
        END IF;
        RETURN NULL;
    END;
$club_audit$ LANGUAGE plpgsql;

CREATE TRIGGER club_audit
AFTER INSERT OR UPDATE OR DELETE ON clubs
    FOR EACH ROW EXECUTE PROCEDURE process_club_audit();