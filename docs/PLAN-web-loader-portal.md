# Project Plan: Web Loader Portal

## Phase 1: Context & Analysis
**Goal:** Create a password-protected web portal to allow users to trigger data loading scripts (`machado/management/commands`) in the background, utilizing the existing `History` model for status tracking.

**Requirements:**
- Standard user authentication (login, logout, password change/reset).
- Dashboard ordering commands sequentially as defined in `docs/`.
- Dynamic checkboxes/dropdowns for relational arguments (from DB).
- File upload and remote URL download support.
- Background execution using `subprocess`.

## Phase 2: Architecture & Components

**Authentication & Account Management:**
- Django's built-in authentication system.
- Protected views with `@login_required`.
- User-facing account management: Password change and password reset.

**User Interface:**
- **Dashboard**: Ordered list of loader commands based on workflow docs.
- **Command Execution Form**: Inputs for parameters, file upload, URL download, and dynamic DB-driven checkboxes for related entities.
- **History Panel**: View displaying a paginated table of the `History` model showing executed commands status.

**Background Execution:**
- Standard `subprocess.Popen` via `python manage.py <command> <args>`.
- History tracking: `exit_code IS NULL` (Running), `0` (Done), `!= 0` (Failed).

## Phase 3: Task Breakdown & Implementation Steps

### Step 1: User Account & Authentication
- [x] Set up login and logout views.
- [x] Configure `PasswordChangeView`, `PasswordResetView`, `PasswordResetDoneView`, `PasswordResetConfirmView`, and `PasswordResetCompleteView`.
- [x] Create corresponding templates for password management.
- [x] Ensure all loader endpoints enforce `login_required`.

### Step 2: Loader Views and Forms
- [x] Parse `docs/` sequence or define static ordered list of commands.
- [x] Create `CommandSelectionView` to list available commands sequentially.
- [x] Create `CommandFormView` which dynamically generates form fields:
  - Text/File inputs for regular arguments.
  - Checkboxes/Dropdowns populated via DB queries for relational arguments.
  - File upload field and URL input field.
- [x] Create utility functions to securely handle file uploads and fetch remote files.

### Step 3: Background Runner Integration
- [x] Process file input (save upload or download from URL) in `CommandFormView` submission.
- [x] Construct the CLI command array (`['python', 'manage.py', ...]`) / switch to `call_command` and threading.
- [x] Spawn process using `subprocess.Popen` / `threading.Thread(target=call_command)`.
- [x] Validate `HistoryCommandMixin` integration handles logging properly.

### Step 4: History Panel
- [x] Create `HistoryListView` fetching `History.objects.all().order_by('-created_at')`.
- [x] Add auto-refresh polling (JavaScript `setInterval`) to update statuses.

## Phase 4: Verification Checklist
- [ ] Unauthenticated users are redirected to login.
- [ ] Commands are ordered exactly as per `docs/`.
- [ ] Selecting a relational parameter like organism generates checkboxes/dropdowns accurately.
- [ ] Uploading a local file successfully triggers the background command.
- [ ] Providing a remote URL successfully downloads the file and triggers the command.
- [ ] Command status correctly transitions from Running to Done/Failed in the History panel.
