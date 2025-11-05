# CRM App Settings
# This file contains cron job configurations for the CRM application

# Application definition
INSTALLED_APPS = [
    'django_crontab',
]

# Cron Jobs Configuration
CRONJOBS = [
    ('*/5 * * * *', 'crm.cron.log_crm_heartbeat'),
    ('0 */12 * * *', 'crm.cron.updatelowstock'),
]
