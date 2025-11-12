# Video Tutorial Scripts

## Tutorial 1: Quick Start Guide (5 minutes)

### Script

**[Opening Scene - Dashboard]**

"Welcome to the PV Testing Protocol Framework. This quick start guide will get you up and running in just 5 minutes."

**[Scene 1 - Login]**

"First, open your web browser and navigate to your installation URL. Enter your username and password provided by your administrator."

*Show login screen and entering credentials*

"Click 'Login' to access the dashboard."

**[Scene 2 - Dashboard Overview]**

"This is your main dashboard. Here you can see:
- Active service requests in the top panel
- Your pending tasks in the middle
- Recent completions at the bottom
- Equipment status on the right"

*Hover over each section*

**[Scene 3 - Creating a Service Request]**

"Let's create a new service request. Click the 'New Service Request' button."

*Click button*

"Fill in the customer information - name, contact person, email, and phone number."

*Fill in example data*

"Next, enter the module details - manufacturer, model, power rating, and quantity."

*Fill in module information*

"Finally, select your testing requirements. You can choose complete standards like IEC 61215, or select individual protocols."

*Check IEC 61215 checkbox*

"Click 'Submit' to create the service request."

*Click submit*

**[Scene 4 - Viewing Service Requests]**

"Your new service request is now visible in the active list. Click on it to view details."

*Click on SR*

"Here you can see the complete information, assigned protocols, and current status."

**[Closing]**

"That's it! You're now ready to use the PV Testing Protocol Framework. For more detailed tutorials, check out the other videos in this series."

---

## Tutorial 2: Protocol Execution Walkthrough (10 minutes)

### Script

**[Opening Scene]**

"In this tutorial, we'll walk through executing a test protocol from start to finish. We'll use PVTP-001, the STC Power Measurement protocol, as our example."

**[Scene 1 - Accessing Tasks]**

"Navigate to 'My Tasks' from the main menu. Here you'll see all protocols assigned to you."

*Show task list*

"Find PVTP-001 in your task list and click on it."

**[Scene 2 - Protocol Overview]**

"Before starting, review the protocol details:
- Test duration: 1-2 hours
- Required equipment: Solar Simulator and I-V Tracer
- Standard: IEC 61215-1:2021"

*Scroll through protocol information*

**[Scene 3 - Equipment Verification]**

"First, verify that the required equipment is available and calibrated. Click 'Check Equipment Status'."

*Click button showing equipment list*

"Green indicators mean the equipment is calibrated and available. If you see red, contact your lab manager."

**[Scene 4 - Starting Execution]**

"Click 'Start Execution' to begin the test."

*Click button*

"Select the module you're testing from the dropdown list."

*Select module*

"Choose your equipment from the available options."

*Select solar simulator and I-V tracer*

**[Scene 5 - Pre-Test Setup]**

"The system now guides you through pre-test procedures:

1. Module Preparation
   - Clean the module surface
   - Allow temperature stabilization
   - Record any visual defects"

*Check boxes as narrating*

"2. Equipment Setup
   - Simulator warm-up (30 minutes)
   - Verify irradiance calibration
   - Check temperature sensors"

*Show equipment setup*

**[Scene 6 - Test Execution]**

"Now we're ready to begin testing. The system will walk you through each step:

Step 1: Position the module on the test platform."

*Show positioning*

"Step 2: Connect electrical leads. The system shows you a diagram of proper connections."

*Show connection diagram*

"Step 3: Verify irradiance. Enter the reading from your reference cell."

*Enter value: 999.8 W/m²*

"Step 4: Monitor temperature. Wait for the module to reach 25°C."

*Show temperature gauge*

"Step 5: Capture I-V curve. Click 'Measure' when ready."

*Click measure button*

"The system automatically captures the I-V curve and extracts key parameters."

*Show I-V curve graph appearing*

**[Scene 7 - Data Entry and Validation]**

"Review the measured values:
- Pmax: 402.5 W
- Voc: 49.52 V
- Isc: 10.24 A
- Fill Factor: 79.45%"

*Highlight each value*

"The system automatically validates the data. Green checkmarks indicate the measurements are within acceptable ranges."

**[Scene 8 - Photos and Documentation]**

"Add photos of your test setup by clicking 'Upload Photo'."

*Show upload dialog*

"Add any relevant notes or observations in the notes field."

*Type example note*

**[Scene 9 - Completing the Test]**

"Once you've verified all data, click 'Complete Test'."

*Click button*

"The system performs final QC checks and determines pass/fail status."

*Show pass/fail screen*

"Click 'Submit for Review' to send the results to your supervisor."

**[Closing]**

"Congratulations! You've successfully completed a protocol execution. The results are now available for report generation."

---

## Tutorial 3: Dashboard Tour (7 minutes)

### Script

**[Opening]**

"Let's take a comprehensive tour of the PV Testing Protocol Framework dashboard and explore all its features."

**[Scene 1 - Main Dashboard]**

"When you first log in, you see the main dashboard with four key areas."

**[Service Requests Panel]**

"The top panel shows active service requests. You can see:
- SR number
- Customer name
- Current status
- Progress percentage
- Estimated completion date"

*Hover over each item*

"Click on any service request to drill down into details."

**[My Tasks Panel]**

"The tasks panel shows protocols assigned to you. Each task card displays:
- Protocol ID and name
- Associated SR number
- Priority level
- Due date"

*Point to each element*

"Tasks are color-coded by priority:
- Red: Urgent
- Orange: High
- Yellow: Normal
- Green: Low"

**[Recent Completions]**

"This panel shows your recently completed tests with pass/fail status."

**[Equipment Status]**

"The equipment panel shows:
- Available equipment
- Calibration status
- Current usage
- Upcoming calibration due dates"

**[Scene 2 - Navigation Menu]**

"The left sidebar provides navigation to all major sections:"

*Hover over each menu item*

"- Dashboard: Your home screen
- Service Requests: Create and manage SRs
- Protocols: Browse protocol catalog
- My Tasks: Your assigned work
- Reports: Generated reports
- Equipment: Equipment management
- Admin: System administration (if authorized)"

**[Scene 3 - Filters and Search]**

"Use the filters at the top to narrow down your view:
- Filter by status
- Filter by customer
- Filter by date range"

*Demonstrate each filter*

"The search bar lets you quickly find service requests by SR number, customer name, or module model."

**[Scene 4 - Notifications]**

"Click the bell icon to view notifications:
- New task assignments
- Approaching deadlines
- Equipment calibration reminders
- System messages"

**[Scene 5 - User Profile]**

"Click your name in the top right to access:
- Profile settings
- Change password
- Notification preferences
- Help documentation
- Logout"

**[Closing]**

"That completes the dashboard tour. You now know how to navigate and use all major features of the system."

---

## Tutorial 4: Admin Configuration (15 minutes)

### Script

**[Opening]**

"This tutorial is for system administrators. We'll cover user management, equipment registration, and system configuration."

**[Scene 1 - User Management]**

"Navigate to Admin → User Management."

*Show user list*

"Here you can see all system users. Let's create a new user."

*Click 'Add User' button*

"Enter the user details:
- Username
- Full name
- Email
- Role (Admin, Engineer, Operator, Viewer)"

*Fill in fields*

"Assign specific permissions if needed. Click 'Create User' to save."

**[Scene 2 - Equipment Registration]**

"Go to Admin → Equipment."

*Show equipment list*

"Click 'Register Equipment' to add new equipment."

*Click button*

"Fill in equipment information:
- Equipment ID
- Type (Solar Simulator, I-V Tracer, etc.)
- Manufacturer and model
- Calibration interval
- Last calibration date"

*Enter information*

"Upload the calibration certificate."

*Upload file*

**[Scene 3 - Protocol Management]**

"Navigate to Admin → Protocols."

*Show protocol list*

"To add a new protocol, click 'Load Protocol'."

*Click button*

"Select the JSON template file and click 'Upload'."

"The system validates the protocol and adds it to the catalog."

**[Scene 4 - Integration Configuration]**

"Go to Admin → Integrations."

*Show integration panel*

"Configure LIMS integration:
- Enter API URL
- Add API key
- Configure field mappings
- Test connection"

*Walk through each step*

"Repeat for QMS and PM system integrations."

**[Scene 5 - System Settings]**

"Under Admin → Settings, you can configure:
- Email notifications
- Report templates
- Data retention policies
- Backup schedules"

**[Closing]**

"You now have the knowledge to fully administer the PV Testing Protocol Framework."

---

## Tutorial 5: Report Generation (8 minutes)

### Script

**[Opening]**

"Learn how to generate comprehensive test reports from your completed protocols."

**[Scene 1 - Accessing Reports]**

"Navigate to the completed service request."

*Click on SR*

"Click the 'Reports' tab."

**[Scene 2 - Report Types]**

"Choose your report type:
- Executive Summary: High-level overview
- Technical Report: Detailed results
- Certificate of Conformance: Pass/fail certificate
- Raw Data Export: Excel/CSV format"

**[Scene 3 - Report Configuration]**

"Select report options:
- Include photos: Yes
- Include raw data: Yes
- Include I-V curves: Yes
- Format: PDF"

*Select options*

"Click 'Generate Report'."

**[Scene 4 - Report Preview]**

"Once generated, you can preview the report before downloading."

*Show report preview*

"The report includes:
- Cover page
- Executive summary
- Test results for each protocol
- Photos and charts
- Signatures"

**[Scene 5 - Downloading and Sharing]**

"Click 'Download' to save the report."

"You can also email the report directly to the customer from here."

*Show email dialog*

**[Closing]**

"Professional reports generated in minutes!"

---

## Tutorial 6: Troubleshooting Common Issues (10 minutes)

### Script

**[Opening]**

"In this tutorial, we'll address common issues and their solutions."

**[Issue 1: Equipment Unavailable]**

"Problem: Equipment shows as 'Unavailable' when trying to start a test.

Solution:
1. Check the equipment calendar
2. If in use, see expected availability time
3. Contact lab manager if needed
4. Reschedule test for later time"

**[Issue 2: Measurement Errors]**

"Problem: Repeated measurement failures or unstable readings.

Solution:
1. Verify equipment calibration status
2. Check all electrical connections
3. Review environmental conditions
4. Retry measurement
5. If persists, contact technical support"

**[Issue 3: Data Entry Validation Errors]**

"Problem: System rejects entered data.

Solution:
1. Review error messages carefully
2. Check data format requirements
3. Verify values are within acceptable ranges
4. Use suggested values if available"

**[Issue 4: Login Problems]**

"Problem: Cannot log in to system.

Solution:
1. Verify username and password
2. Check Caps Lock is off
3. Clear browser cache
4. Try different browser
5. Contact admin for password reset"

**[Issue 5: Slow Performance]**

"Problem: System is running slowly.

Solution:
1. Close unused browser tabs
2. Clear browser cache
3. Check internet connection
4. Try during off-peak hours
5. Contact IT if persists"

**[Closing]**

"For additional support, contact the help desk or consult the documentation."

---

**Document Version**: 1.0
**Last Updated**: 2025-11-12
**Total Tutorial Length**: ~55 minutes
