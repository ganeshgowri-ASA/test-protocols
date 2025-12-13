# Sample Inventory - Warehouse Management Implementation
## UI Screenshots & Feature Overview

### Tab 1: 📊 Inventory Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  Sample Inventory - Warehouse Management                                    │
│  Comprehensive warehouse & location tracking                                │
└─────────────────────────────────────────────────────────────────────────────┘

[📊 Inventory Overview] [🔍 Search & Locate] [📦 Transfer Samples] [📈 Reports]

┌─────────────────────────────────────────────────────────────────────────────┐
│ 📊 Real-Time Inventory Dashboard                                            │
└─────────────────────────────────────────────────────────────────────────────┘

┌───────────────┬───────────────┬───────────────┬───────────────┬──────────────┐
│ Total Samples │  In Storage   │  In Testing   │  Checked Out  │  Locations   │
│      247      │      189      │       42      │       16      │      24      │
└───────────────┴───────────────┴───────────────┴───────────────┴──────────────┘

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📦 Storage Capacity Utilization
▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓░░░░░░░░░░░░░░  72.4% Utilized (189/261)
                                                              Utilization
✓ Storage capacity is within normal range                        72.4%

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🏢 Storage Locations Status

▼ 🏢 Building A (12 locations)
   ┌─────────────────────────┬─────────────────────────┬─────────────────────────┐
   │ 🟢 BuildingA-R101-R1-S1 │ 🟡 BuildingA-R101-R1-S2 │ 🔴 BuildingA-R101-R1-S3 │
   │ Room 101/R1/S1          │ Room 101/R1/S2          │ Room 101/R1/S3          │
   │ 25/50 samples           │ 42/50 samples           │ 48/50 samples           │
   │                         │                         │ 🌡️ 20°C - 25°C         │
   └─────────────────────────┴─────────────────────────┴─────────────────────────┘

▼ 🏢 Building B (8 locations)
   ┌─────────────────────────┬─────────────────────────┬─────────────────────────┐
   │ 🟢 BuildingB-R201-R1-S1 │ 🟢 BuildingB-R201-R1-S2 │ 🟢 BuildingB-R202-R1-S1 │
   │ Room 201/R1/S1          │ Room 201/R1/S2          │ Room 202/R1/S1          │
   │ 35/40 samples           │ 15/40 samples           │ 12/60 samples           │
   │ 🌡️ 20°C - 25°C         │ 🌡️ 20°C - 25°C         │ 💧 Humidity Controlled  │
   └─────────────────────────┴─────────────────────────┴─────────────────────────┘

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔄 Recent Inventory Activity

Sample ID          │ Location               │ Status    │ Condition │ Updated
SAMPLE-2024-00245  │ BuildingA/R101/R1/S1  │ in_stock  │ excellent │ 12-04 10:25
SAMPLE-2024-00244  │ BuildingA/R101/R1/S2  │ in_stock  │ good      │ 12-04 10:18
SAMPLE-2024-00243  │ BuildingB/R201/R1/S1  │ in_test   │ good      │ 12-04 10:10
```

---

### Tab 2: 🔍 Search & Locate

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ 🔍 Search & Locate Samples                                                  │
└─────────────────────────────────────────────────────────────────────────────┘

Search Methods:
⚪ Sample ID   ⚫ QR/Barcode Scan   ⚪ Client Name   ⚪ Location   ⚪ Status

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📷 Barcode/QR Scanner

┌─────────────────────────────────────────────────────────────────────────────┐
│ Scan or Enter QR/Barcode                                                    │
│ [SAMPLE-2024-00245_________________]  🔍                                    │
│ ℹ️  Use a barcode scanner or manually type the code                         │
└─────────────────────────────────────────────────────────────────────────────┘

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📋 Search Results

▼ 📦 SAMPLE-2024-00245 - Solar PV Module

   ┌────────────────────────────────────────┬────────────────────────────────────────┐
   │ Sample Information                     │ Location & Storage                     │
   ├────────────────────────────────────────┼────────────────────────────────────────┤
   │ • ID: SAMPLE-2024-00245                │ • Location: BuildingA/R101/R1/S1       │
   │ • Type: Solar PV Module                │ • Storage Status: in_stock             │
   │ • Manufacturer: SolarTech Inc.         │ • Condition: excellent                 │
   │ • Model: ST-500W                       │ • Checked Out: No ✓                    │
   │ • Serial: ST20240245                   │                                        │
   │ • Status: allocated                    │                                        │
   └────────────────────────────────────────┴────────────────────────────────────────┘
   
   Quick Actions
   [📍 View Location Map]  [🔄 Transfer Location]  [📊 View History]
```

---

### Tab 3: 📦 Transfer Samples

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ 📦 Transfer Samples Between Locations                                       │
└─────────────────────────────────────────────────────────────────────────────┘

[Single Transfer] [Batch Transfer] [Manage Locations]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Transfer Single Sample

┌─────────────────────────────────────────┬─────────────────────────────────────────┐
│ Select Sample to Transfer               │ Destination Location                    │
│ [SAMPLE-2024-00245 - BuildingA...  ▼]   │ [BuildingB-R201-R1-S2 (15/40)      ▼]   │
└─────────────────────────────────────────┴─────────────────────────────────────────┘

Transfer Reason: [Reorganization                                            ▼]

Transfer Notes:
┌─────────────────────────────────────────────────────────────────────────────┐
│ Moving to temperature-controlled storage for upcoming environmental tests  │
└─────────────────────────────────────────────────────────────────────────────┘

                        [📦 Transfer Sample]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

BATCH TRANSFER TAB:

💡 Select multiple samples to transfer them all to the same location at once

┌─────────────────────────────────────────────────────────────────────────────┐
│ Select │ Sample ID         │ Current Location      │ Status    │ Condition  │
├────────┼───────────────────┼───────────────────────┼───────────┼────────────┤
│   ☑    │ SAMPLE-2024-00243 │ BuildingA/R101/R1/S1 │ in_stock  │ good       │
│   ☑    │ SAMPLE-2024-00244 │ BuildingA/R101/R1/S1 │ in_stock  │ excellent  │
│   ☐    │ SAMPLE-2024-00245 │ BuildingA/R101/R1/S2 │ in_stock  │ good       │
│   ☑    │ SAMPLE-2024-00246 │ BuildingA/R101/R1/S3 │ in_stock  │ fair       │
└─────────────────────────────────────────────────────────────────────────────┘

ℹ️  3 sample(s) selected

Destination Location: [BuildingB-R202-R1-S1 (12/60) - Available: 48    ▼]
Transfer Reason: [Return to Storage                                    ▼]

                     [📦 Transfer 3 Sample(s)]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

MANAGE LOCATIONS TAB:

▼ ➕ Add New Storage Location

   Location Details
   
   ┌──────────────────┬──────────────────┬──────────────────┐
   │ Building *       │ Room *           │ Rack *           │
   │ [Building C____] │ [Room 301______] │ [R1____________] │
   └──────────────────┴──────────────────┴──────────────────┘
   ┌──────────────────┬──────────────────┐
   │ Shelf *          │ Capacity         │
   │ [S1____________] │ [50___]          │
   └──────────────────┴──────────────────┘
   
   ℹ️  Location Code: BuildingC-Room301-R1-S1
   
   ☑ Temperature Controlled
     Min Temperature (°C): [18.0]
     Max Temperature (°C): [22.0]
   
   ☐ Humidity Controlled
   
   Description: [Storage for temperature-sensitive samples_____________]
   
                          [➕ Add Location]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Existing Storage Locations

▼ 🟢 BuildingA-Room101-R1-S1 - 🟢 50.0% Full

   ┌──────────────────────┬──────────────────────┬──────────────────────┐
   │ Location             │ Capacity             │ Environmental        │
   ├──────────────────────┼──────────────────────┼──────────────────────┤
   │ • Building: BuildingA│ • Total: 50          │ Status: Active ✓     │
   │ • Room: Room101      │ • Current: 25        │                      │
   │ • Rack: R1           │ • Available: 25      │                      │
   │ • Shelf: S1          │ ▓▓▓▓▓▓▓▓▓▓░░░░░░░░░░ │                      │
   └──────────────────────┴──────────────────────┴──────────────────────┘
   
   [🔄 Toggle Status]  [🗑️ Delete]
```

---

### Tab 4: 📈 Reports

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ 📈 Inventory Reports & Analytics                                            │
└─────────────────────────────────────────────────────────────────────────────┘

Select Report Type: [Location Utilization                                  ▼]

                       [📊 Generate Report]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 Location Utilization Report
Generated: 2024-12-04 10:35:42

┌──────────────────────────────────────────────────────────────────────────────┐
│ Location Code        │ Building │ Room  │ Rack │ Shelf │ Capacity │ Current │
├──────────────────────┼──────────┼───────┼──────┼───────┼──────────┼─────────┤
│ BuildingA-R101-R1-S1 │ BuildingA│ R101  │ R1   │ S1    │    50    │   25    │
│ BuildingA-R101-R1-S2 │ BuildingA│ R101  │ R1   │ S2    │    50    │   42    │
│ BuildingA-R101-R1-S3 │ BuildingA│ R101  │ R1   │ S3    │    50    │   48    │
│ BuildingB-R201-R1-S1 │ BuildingB│ R201  │ R1   │ S1    │    40    │   35    │
│ BuildingB-R201-R1-S2 │ BuildingB│ R201  │ R1   │ S2    │    40    │   15    │
│ BuildingB-R202-R1-S1 │ BuildingB│ R202  │ R1   │ S1    │    60    │   12    │
└──────────────────────────────────────────────────────────────────────────────┘

📊 Utilization Chart:

    Storage Location Utilization
    
    50 ┤                  ████
    40 ┤  ████    ████    ████    ████
    30 ┤  ████    ████    ████    ████
    20 ┤  ████    ████    ████    ████    ████
    10 ┤  ████    ████    ████    ████    ████    ████
     0 ┼────────────────────────────────────────────────
       │  S1      S2      S3      S1      S2      S1
       │  BuildingA-R101          BuildingB-R201  B-R202

**📥 Export Options:**
[📥 Download Report (Excel)]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

OVERDUE CHECK-OUTS REPORT:

⚠️ Overdue Check-outs Report
Generated: 2024-12-04 10:36:15

⚠️ 2 sample(s) overdue

┌──────────────────────────────────────────────────────────────────────────────┐
│ Sample ID       │ Location │ Checked Out │ Expected   │ Days    │ Reason     │
│                 │          │ Date        │ Return     │ Overdue │            │
├─────────────────┼──────────┼─────────────┼────────────┼─────────┼────────────┤
│ SAMPLE-2024-001 │ Lab-R1   │ 2024-11-20  │ 2024-11-27 │   7     │ Testing    │
│ SAMPLE-2024-015 │ Lab-R2   │ 2024-11-25  │ 2024-12-02 │   2     │ Inspection │
└──────────────────────────────────────────────────────────────────────────────┘

[📥 Download Report (Excel)]
```

---

## Summary of UI Features

### Visual Indicators
- 🟢 **Green**: Healthy capacity (<75%)
- 🟡 **Yellow**: Warning capacity (75-90%)
- 🔴 **Red**: Critical capacity (>90%)
- 🌡️ **Temperature icon**: Temperature controlled
- 💧 **Droplet icon**: Humidity controlled

### Interactive Elements
- ✅ Checkboxes for batch selection
- 📊 Progress bars for capacity visualization
- 🔍 Search inputs with live filtering
- ▼ Dropdown selectors for location hierarchy
- 📥 Download buttons for reports

### Key User Actions
1. **Search** samples by multiple methods
2. **Transfer** samples individually or in batches
3. **Manage** storage locations (add/edit/delete)
4. **Monitor** capacity in real-time
5. **Generate** and export reports
6. **Track** overdue samples
7. **View** environmental controls

All features follow Streamlit's design patterns and maintain consistency with the existing application interface.
