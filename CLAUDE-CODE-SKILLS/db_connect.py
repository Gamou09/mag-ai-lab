import os


def read_config():
    return {
        "host": os.getenv("DB_HOST", "localhost"),
        "port": os.getenv("DB_PORT", "5432"),
        "database": os.getenv("DB_NAME", "example_db"),
        "user": os.getenv("DB_USER", "postgres"),
        "password": os.getenv("DB_PASSWORD", ""),
    }


def connect_db():
    config = read_config()
    print(
        f"Simulated connection to {config['database']} "
        f"at {config['host']}:{config['port']}"
    )
    return config
