DO
$$
BEGIN
   IF NOT EXISTS (
      SELECT FROM pg_database WHERE datname = 'swe'
   ) THEN
      PERFORM dblink_exec('dbname=postgres', 'CREATE DATABASE swe');
   END IF;
END
$$;
