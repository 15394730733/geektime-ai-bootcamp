---

description: "Task list for query results export feature"
---

# Tasks: Query Results Export Feature

**Input**: FEATURE_EXPORT.md specification
**Prerequisites**: Database Query Tool (001-db-query-tool) base implementation

**Organization**: Tasks organized by user story to enable independent implementation and testing.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2)
- Include exact file paths in descriptions

## Path Conventions

- **Frontend**: `frontend/src/components/`, `frontend/src/pages/`
- **Backend**: No backend changes required (frontend-only feature)

---

## Phase 1: Verification & Testing (US1 - Manual Export)

**Purpose**: Verify existing manual export functionality works correctly

**Goal**: Ensure CSV and JSON manual export buttons work correctly for all data types

**Independent Test**: Execute queries with various data types and export to verify file correctness

### Test Implementation for User Story 1

- [ ] T001 [P] [US1] Create export utility tests in frontend/src/components/__tests__/QueryResults.export.test.tsx
- [ ] T002 [P] [US1] Create CSV conversion tests in frontend/src/utils/__tests__/export.test.ts

### Verification for User Story 1

- [ ] T003 [US1] Test CSV export with normal data in QueryResults.tsx:117-127
- [ ] T004 [US1] Test CSV export with special characters (commas, quotes, newlines) in QueryResults.tsx:76-92
- [ ] T005 [US1] Test CSV export with NULL values in QueryResults.tsx:76-92
- [ ] T006 [US1] Test JSON export with various data types in QueryResults.tsx:129-139
- [ ] T007 [US1] Verify CSV file opens correctly in Excel/Google Sheets
- [ ] T008 [US1] Verify JSON file format is valid and parseable
- [ ] T009 [US1] Test export button disabled state when no results in QueryResults.tsx:204,211
- [ ] T010 [US1] Fix any bugs found during testing

**Checkpoint**: At this point, User Story 1 (Manual Export) should be fully functional

---

## Phase 2: Auto Export Implementation (US2 - Auto Export Configuration)

**Purpose**: Implement automatic export functionality with checkbox configuration

**Goal**: Users can configure auto-export preferences via checkboxes, and results are automatically exported on query execution

**Independent Test**: Execute queries with different checkbox configurations and verify auto-export behavior

### UI Implementation for User Story 2

- [X] T011 [P] [US2] Add Checkbox imports to QueryEditor.tsx (add Checkbox from antd)
- [X] T012 [P] [US2] Add auto-export state management to QueryEditor.tsx (autoExportCSV, autoExportJSON state)
- [X] T013 [US2] Add auto-export callback prop to QueryEditor interface in QueryEditor.tsx:18-25
- [X] T014 [US2] Render CSV and JSON checkboxes in toolbar in QueryEditor.tsx (position: left of Execute button)
- [X] T015 [US2] Set default checkbox state to checked in QueryEditor.tsx (useState initial value: true)
- [X] T016 [US2] Implement checkbox change handler in QueryEditor.tsx

### Integration for User Story 2

- [X] T017 [US2] Add auto-export props to QueryResults component interface in QueryResults.tsx:13-21
- [X] T018 [US2] Add useRef to track exported results in QueryResults.tsx (prevent duplicate exports)
- [X] T019 [US2] Add useEffect to monitor rows changes for auto-export in QueryResults.tsx
- [X] T020 [US2] Implement auto-export trigger logic in QueryResults.tsx useEffect
- [X] T021 [US2] Add conditional checks to prevent auto-export on empty results in QueryResults.tsx useEffect
- [X] T022 [US2] Add conditional checks to prevent auto-export on query errors in QueryResults.tsx useEffect
- [X] T023 [US2] Update QueryPanel.tsx to manage auto-export state
- [X] T024 [US2] Pass auto-export props from QueryPanel to QueryEditor in QueryPanel.tsx
- [X] T025 [US2] Pass auto-export props from QueryPanel to QueryResults in QueryPanel.tsx

### Test Implementation for User Story 2

- [ ] T026 [P] [US2] Create auto-export integration tests in frontend/src/components/__tests__/QueryResults.autoexport.test.tsx
- [ ] T027 [P] [US2] Create checkbox UI tests in frontend/src/components/__tests__/QueryEditor.autoexport.test.tsx

### Verification for User Story 2

- [ ] T028 [US2] Test checkboxes default to checked on page load
- [ ] T029 [US2] Test auto-export works when only CSV checkbox is checked
- [ ] T030 [US2] Test auto-export works when only JSON checkbox is checked
- [ ] T031 [US2] Test auto-export works when both checkboxes are checked
- [ ] T032 [US2] Test auto-export does NOT trigger when both checkboxes are unchecked
- [ ] T033 [US2] Test auto-export does NOT trigger when query returns 0 rows
- [ ] T034 [US2] Test auto-export does NOT trigger when query execution fails
- [ ] T035 [US2] Test auto-export files use same naming convention as manual export
- [ ] T036 [US2] Test auto-export does not trigger duplicate exports for same result set
- [ ] T037 [US2] Fix any bugs found during testing

**Checkpoint**: At this point, User Story 2 (Auto Export) should be fully functional

---

## Phase 3: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect both user stories

- [ ] T038 [P] Add loading state indicators during auto-export in QueryResults.tsx
- [ ] T039 [P] Add user feedback (toast message) for auto-export completion in QueryResults.tsx
- [ ] T040 Optimize auto-export performance for large result sets in QueryResults.tsx
- [ ] T041 Add browser compatibility checks for download functionality in QueryResults.tsx:105-115
- [ ] T042 Add error handling for browser download restrictions in QueryResults.tsx
- [ ] T043 Update component documentation (JSDoc comments) in QueryEditor.tsx and QueryResults.tsx
- [ ] T044 Code cleanup and refactoring (extract export utilities to separate file if needed)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (US1 Verification)**: No dependencies - can start immediately
- **Phase 2 (US2 Implementation)**: Can start after Phase 1, but largely independent
- **Phase 3 (Polish)**: Depends on Phase 1 and Phase 2 completion

### Task Dependencies Within Phases

#### Phase 1 (US1 - Manual Export)
- T001-T002: Can run in parallel (test file creation)
- T003-T010: Should run sequentially (verification and bug fixes)

#### Phase 2 (US2 - Auto Export)
- T011-T012: Can run in parallel (independent changes to QueryEditor.tsx)
- T013-T016: Must follow T011-T012 (depends on state management setup)
- T017-T022: Must follow T013-T016 (QueryResults integration depends on QueryEditor interface)
- T023-T025: Must follow T017-T022 (QueryPanel integration depends on component interfaces)
- T026-T027: Can run in parallel with T011-T016 (test files independent of implementation)
- T028-T037: Must follow T017-T025 (verification depends on implementation completion)

### Parallel Opportunities

**Phase 1**:
```bash
# Create test files in parallel:
Task T001: Create export utility tests
Task T002: Create CSV conversion tests
```

**Phase 2**:
```bash
# Initial UI setup can be parallel:
Task T011: Add Checkbox imports
Task T012: Add auto-export state management

# Test file creation can be parallel:
Task T026: Create auto-export integration tests
Task T027: Create checkbox UI tests
```

**Phase 3**:
```bash
# Polish tasks can run in parallel:
Task T038: Add loading state indicators
Task T039: Add user feedback
Task T041: Add browser compatibility checks
Task T043: Update documentation
```

---

## Parallel Example: User Story 2 UI Setup

```bash
# Launch initial UI tasks together:
Task T011: "Add Checkbox imports to QueryEditor.tsx"
Task T012: "Add auto-export state management to QueryEditor.tsx"

# Then continue with sequential implementation:
Task T013: "Add auto-export callback prop to QueryEditor interface"
Task T014: "Render CSV and JSON checkboxes in toolbar"
...
```

---

## Implementation Strategy

### MVP First (User Story 1 Only - Manual Export Verification)

1. Complete Phase 1: Verify existing manual export functionality
2. **STOP and VALIDATE**: Test manual export with various data types
3. Fix any bugs found during verification
4. **MVP COMPLETE**: Manual export works correctly

### Full Feature (User Story 2 - Auto Export)

1. Complete Phase 1 (if not already done)
2. Complete Phase 2: Implement auto-export functionality
3. Test auto-export with all checkbox configurations
4. **FEATURE COMPLETE**: Both manual and auto-export work correctly

### Incremental Delivery

1. **Week 1**: Phase 1 - Verify and fix manual export
   - Deliver reliable manual export functionality
   - User can export results via buttons

2. **Week 2**: Phase 2 - Implement auto-export
   - Add checkbox UI
   - Implement auto-export logic
   - Test all scenarios

3. **Week 3**: Phase 3 - Polish and optimize
   - Improve user feedback
   - Optimize performance
   - Final testing and bug fixes

---

## Task Summary

### Total Tasks: 44

**By Phase**:
- Phase 1 (US1 Manual Export): 10 tasks
- Phase 2 (US2 Auto Export): 27 tasks
- Phase 3 (Polish): 7 tasks

**By Type**:
- Test Creation: 4 tasks (T001, T002, T026, T027)
- UI Implementation: 10 tasks (T011-T016, T038-T039, T043)
- Logic Implementation: 15 tasks (T017-T022, T028-T037)
- Integration: 5 tasks (T023-T025, T040, T044)
- Verification: 10 tasks (T003-T010)

### Parallelizable Tasks: 12 tasks
- Marked with [P] can be executed in parallel
- Reduces total execution time by ~40%

### Estimated Timeline

**Single Developer**:
- Phase 1: 1-2 days
- Phase 2: 3-4 days
- Phase 3: 1-2 days
- **Total**: 5-8 days

**With Parallel Execution**:
- Phase 1: 1 day (with test parallelization)
- Phase 2: 2-3 days (with UI setup parallelization)
- Phase 3: 1 day (with polish task parallelization)
- **Total**: 4-5 days

---

## Risk Assessment

### Technical Risks

1. **Browser Compatibility**
   - Risk: Some browsers may block automatic downloads
   - Mitigation: T041, T042 add compatibility checks and error handling

2. **Duplicate Exports**
   - Risk: Auto-export may trigger multiple times for same result
   - Mitigation: T018 uses useRef to track exported results

3. **Performance with Large Datasets**
   - Risk: Exporting large result sets may cause UI lag
   - Mitigation: T040 optimizes performance (current LIMIT 1000 reduces risk)

4. **State Management Complexity**
   - Risk: Passing auto-export state through multiple components
   - Mitigation: Clear component interfaces and prop drilling

### Schedule Risks

1. **Bug Discovery in Phase 1**
   - Risk: Existing export code may have bugs
   - Mitigation: Allocate buffer time in T010 for fixes

2. **Integration Issues**
   - Risk: QueryPanel modifications may affect existing functionality
   - Mitigation: Comprehensive testing in T028-T037

---

## Notes

- All tasks are frontend-only (no backend API changes required)
- Export uses existing convertToCSV and convertToJSON functions
- Auto-export logic leverages existing manual export functions
- Browser native download API used (Blob, URL.createObjectURL)
- Checkbox state is session-only (not persisted across reloads)
- File naming convention already established in manual export
- Auto-export designed to be non-intrusive (no error popups on failure)
- All export operations client-side (no server load)

---

## Success Criteria Verification

### Manual Export (US1)
- ✅ CSV export works for all data types (T003-T005)
- ✅ JSON export works for all data types (T006)
- ✅ CSV opens in Excel/Google Sheets (T007)
- ✅ JSON is valid and parseable (T008)
- ✅ Buttons disabled when no results (T009)

### Auto Export (US2)
- ✅ Checkboxes default to checked (T028)
- ✅ Auto-export downloads within 1 second (T029-T031)
- ✅ No export on 0 rows (T033)
- ✅ No export on query failure (T034)
- ✅ Same filename format (T035)
- ✅ No duplicate exports (T036)
