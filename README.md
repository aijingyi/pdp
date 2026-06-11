# PDP Reports

A tool to automatically generate Performance Data Preview (PDP) reports for Wind River Linux team members. It collects data from Jira, LTAF, and Git repositories to produce yearly performance summaries.

## Features

- **Git commit statistics** - Counts new/updated test cases, RCA commits across multiple test repositories
- **Jira defect reports** - Submitted defects, valid ratio, priority breakdown, test-blocking defects
- **Verified defects** - Defects closed/verified by the user
- **Test run summary** - Collected from LTAF (Linux Test Automation Framework)
- **Batch generation** - Generate reports for the entire team at once

## Usage

### Single user (current user, current year)

```bash
./pdp-reports.py
```

### Specify user and year

```bash
./pdp-reports.py -u kliang -y 2024
```

### Options

| Option | Description | Default |
|--------|-------------|---------|
| `-u` | Unix username | Current user |
| `-y` | Report year | Current year |
| `-l` | Include Jira links (yes/no) | yes |
| `-c` | Include git commit summary (yes/no) | yes |

### Generate reports for all team members

```bash
./get-all-pdp.sh
```

## Report Contents

1. New test case commits
2. Updated test case commits
3. Submitted defects list (with priority and valid ratio)
4. Verified defects list
5. Test run list
6. Feature User Story lists
7. Internal trainings and technical documentations
8. Linux test improvements
9. Highlights
10. Other noteworthy data

## Output

Reports are saved to `reports/<year>/pdp_reports_<username>_<year>.txt`

## Git Repositories

- http://lxgit.wrs.com/cgit/users/kliang/pdp.git/
- http://lxgit.wrs.com/cgit/users/kliang/pdp-reports.git/

## Contact

kai.liang@windriver.com
