user=postgres.mzwmsyljdvlodaxqqqoz password=legacywebhub10 host=aws-0-eu-central-1.pooler.supabase.com port=6543 dbname=postgres

DATABASES = {
    # For Render or production
    'default': dj_database_url.parse('postgresql://postgres.mzwmsyljdvlodaxqqqoz:legacywebhub10@aws-0-eu-central-1.pooler.supabase.com:6543/postgres'),
    'postgres': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'postgres',
        'USER': 'postgres.mzwmsyljdvlodaxqqqoz',
        'PASSWORD': 'legacywebhub10',
        'HOST': 'aws-0-eu-central-1.pooler.supabase.com',
        'PORT': 6543
    },
    'sqlite': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}