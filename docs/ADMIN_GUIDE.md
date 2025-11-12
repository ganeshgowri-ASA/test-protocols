# Administrator Guide

## System Administration

### User Management

#### Adding Users

```bash
python manage.py create_user \
    --username john.smith \
    --email john.smith@company.com \
    --full-name "John Smith" \
    --role engineer
```

Roles:
- **admin**: Full system access
- **manager**: Approve reports, manage projects
- **engineer**: Execute protocols, generate reports
- **operator**: Execute assigned protocols
- **viewer**: Read-only access

#### Managing Permissions

```python
# Grant specific permissions
python manage.py grant_permission \
    --user john.smith \
    --permission execute_protocols
```

### Equipment Management

#### Registering Equipment

1. Navigate to **Admin → Equipment**
2. Click **"Add Equipment"**
3. Enter details:
   - Equipment ID
   - Type (Solar Simulator, IV Tracer, etc.)
   - Manufacturer and model
   - Calibration interval
   - Last calibration date
4. Upload calibration certificate
5. Click **"Save"**

#### Calibration Tracking

System automatically:
- Tracks calibration due dates
- Sends reminders 30 days before due
- Flags overdue equipment
- Prevents use of expired equipment

### Protocol Management

#### Adding New Protocols

1. Create JSON template in `templates/protocols/`
2. Load protocol:
   ```bash
   python manage.py load_protocol \
       --file templates/protocols/PVTP-055.json
   ```
3. Create UI page in `pages/protocol_execution/`
4. Test protocol execution
5. Publish to production

#### Updating Protocols

```bash
python manage.py update_protocol \
    --protocol-id PVTP-001 \
    --version 1.1 \
    --file templates/protocols/PVTP-001_v1.1.json
```

### System Monitoring

#### Health Checks

```bash
# Check system health
python manage.py health_check

# Check database connectivity
python manage.py check_db

# Check integrations
python manage.py check_integrations
```

#### Performance Monitoring

- Monitor dashboard response times
- Track API latency
- Review database query performance
- Check storage usage

### Backup and Recovery

#### Database Backup

```bash
# Daily automated backup
0 2 * * * /usr/local/bin/backup_database.sh

# Manual backup
pg_dump pv_testing > backup_$(date +%Y%m%d).sql
```

#### File Backup

```bash
# Backup reports and data
rsync -av /data/pv_testing/ /backup/pv_testing/
```

#### Recovery

```bash
# Restore database
psql pv_testing < backup_20251112.sql

# Restore files
rsync -av /backup/pv_testing/ /data/pv_testing/
```

### Integration Management

#### LIMS Configuration

1. Navigate to **Admin → Integrations → LIMS**
2. Enter LIMS API details
3. Configure field mappings
4. Test connection
5. Enable synchronization

#### Troubleshooting Integrations

```bash
# View integration logs
tail -f logs/integrations.log

# Test LIMS connection
python manage.py test_lims_connection

# Retry failed syncs
python manage.py retry_failed_syncs --system lims
```

### Security Management

#### SSL Certificate

```bash
# Install certificate
sudo cp cert.pem /etc/ssl/certs/
sudo cp key.pem /etc/ssl/private/

# Update nginx config
sudo nano /etc/nginx/sites-available/pv-testing
sudo nginx -t
sudo systemctl reload nginx
```

#### Password Policies

Configure in `config/security.yaml`:
```yaml
password_policy:
  min_length: 12
  require_uppercase: true
  require_numbers: true
  require_special: true
  expiry_days: 90
```

### Maintenance

#### System Updates

```bash
# Update system
./deploy/update.sh

# Update dependencies only
pip install -r requirements.txt --upgrade

# Run migrations
python manage.py db upgrade
```

#### Log Rotation

```bash
# Configure logrotate
sudo nano /etc/logrotate.d/pv-testing
```

### Troubleshooting

#### Common Issues

1. **Database Connection Errors**
   - Check PostgreSQL service
   - Verify credentials
   - Check network connectivity

2. **Slow Performance**
   - Review database indexes
   - Check disk space
   - Monitor CPU/RAM usage

3. **Integration Failures**
   - Verify API credentials
   - Check network access
   - Review logs

---

**Version**: 1.0.0
**Last Updated**: 2025-11-12
