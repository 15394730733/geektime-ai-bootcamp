# Testing Plan: Database Selector Fix

## Changes Made

### 1. AppStateContext.tsx
- Added `switchingDatabase` boolean to state
- Added `START_DATABASE_SWITCH` and `COMPLETE_DATABASE_SWITCH` actions
- Enhanced `selectDatabase` function with:
  - Duplicate selection check
  - Database switching state management
  - Success message after switch
  - Console logging for debugging
- Enhanced `loadMetadata` function with console logging

### 2. Query.tsx
- Updated Select component with:
  - Explicit onChange handler with logging
  - `disabled` prop when switching
  - `loading` prop includes `switchingDatabase` state
  - `showSearch` for better UX
  - `optionFilterProp` and `filterOption` for search functionality

## Manual Testing Steps

### Test 1: Basic Database Selection
1. Open the application and navigate to Query page
2. Open browser console (F12)
3. Click on the database selector dropdown
4. Select a different database (e.g., switch from "test2" to "test")
5. **Expected Results:**
   - Console shows: "Select onChange triggered with value: test"
   - Console shows: "Selecting database: test Current: test2"
   - Select dropdown immediately shows the new database name
   - Success message appears: "Switched to database: test"
   - Metadata panel updates with new database schema
   - No errors in console

### Test 2: Same Database Selection
1. With a database already selected
2. Click on the selector and choose the same database
3. **Expected Results:**
   - Console shows: "Database already selected, skipping"
   - No unnecessary metadata reload
   - No success message (since nothing changed)

### Test 3: Rapid Database Switching
1. Quickly switch between multiple databases
2. Click: test2 → test → test2 → test
3. **Expected Results:**
   - Each switch is handled correctly
   - No race conditions
   - Final selection matches the last clicked database
   - Metadata matches the final selection

### Test 4: Loading States
1. Switch to a database with large metadata
2. Observe the UI during loading
3. **Expected Results:**
   - Select component shows loading spinner
   - Select is disabled during switch
   - Cannot click on selector while loading
   - Loading state clears after metadata loads

### Test 5: Error Handling
1. Disconnect backend or cause a metadata load error
2. Try to switch databases
3. **Expected Results:**
   - Error message displayed
   - Select re-enables after error
   - Previous database selection maintained
   - Can retry selection

### Test 6: Mobile View
1. Resize browser to mobile width (< 768px)
2. Test database selection
3. **Expected Results:**
   - Selector works correctly in mobile layout
   - Success message visible
   - Metadata drawer updates correctly

### Test 7: URL Parameter
1. Navigate to `/query?db=test`
2. **Expected Results:**
   - Database auto-selected from URL
   - Metadata loads automatically
   - Select shows correct database

## Console Output Verification

Expected console logs during a successful switch:

```
Select onChange triggered with value: test
Selecting database: test Current: test2
Loading metadata for database: test
Metadata loaded successfully: {tables: [...], views: [...]}
```

## Success Criteria

- [ ] Database selector visually updates immediately on click
- [ ] Metadata panel shows correct schema for selected database
- [ ] Success message appears after switch
- [ ] Loading state prevents multiple rapid clicks
- [ ] No console errors
- [ ] Works in both desktop and mobile layouts
- [ ] Search functionality works in dropdown
- [ ] Duplicate selections are handled gracefully

## Known Issues to Watch For

1. **Race Condition**: If switching very rapidly, ensure the final state matches the last selection
2. **Memory Leaks**: Check that old metadata is properly cleared
3. **Event Bubbling**: Ensure onChange fires correctly and only once per selection

## Debugging Tips

If issues persist:

1. Check console for all log messages
2. Verify `state.selectedDatabase` in React DevTools
3. Check network tab for metadata API calls
4. Verify Select component's `value` prop matches state
5. Check if `onChange` is being called multiple times

## Rollback Procedure

If critical issues are found:

```bash
git checkout HEAD -- w2/sth-db-query/frontend/src/contexts/AppStateContext.tsx
git checkout HEAD -- w2/sth-db-query/frontend/src/pages/Query.tsx
```

Then restart the frontend development server.
