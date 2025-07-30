# V2T Development Workflow

**Document Version**: 1.0  
**Last Updated**: 2025-07-30  
**Purpose**: Standard workflow procedures for V2T development

---

## 🔄 **Mandatory Task Completion Workflow**

**CRITICAL**: Every development task MUST follow this 4-step process:

### Step 1: Implement the Task ⚡
- Complete implementation according to Task_breakdown.md specifications
- Follow Implementation.md coding standards
- Ensure code is tested and functional

### Step 2: Commit Implementation 📝
```bash
git add .
git commit -m "feat(module): implement specific functionality

- Detailed description of what was implemented
- Reference to Task_breakdown.md task
- Any important technical notes

Completes Phase X.Y.Z: Task description
✅ Task completed from Task_breakdown.md"
```

### Step 3: Update Task_breakdown.md ✅
- Change `[ ]` to `[x]` for completed task
- Add completion timestamp: `*(Completed: YYYY-MM-DD)*`
- Mark parent sections complete when all subtasks done
- Update document version number

### Step 4: Commit Progress Tracking 📊
```bash
git add Docs/Task_breakdown.md
git commit -m "docs(tracking): mark [task description] as completed

- Update Task_breakdown.md with completion status
- Add completion timestamp for tracking
- Mark Phase X.Y as [percentage]% complete

✅ Progress tracking updated"
```

---

## 📋 **Task Completion Format Examples**

### Individual Task Completion
**Before:**
```markdown
- [ ] Implement start_recording() method
```

**After:**
```markdown
- [x] Implement start_recording() method *(Completed: 2025-07-30)*
```

### Section Completion
**Before:**
```markdown
#### 2.1 Audio Capture (`src/audio/recorder.py`)
```

**After:**
```markdown
#### 2.1 Audio Capture (`src/audio/recorder.py`) ✅
```

### Phase Completion
**Before:**
```markdown
### Phase 2: Audio Processing Module
**Goal**: Implement audio capture and processing functionality
```

**After:**
```markdown
### Phase 2: Audio Processing Module ✅ **COMPLETED**
**Goal**: Implement audio capture and processing functionality
**Completed**: 2025-07-30 23:45
```

---

## 🎯 **Development Session Workflow**

### Daily Development Pattern
1. **Start Session**
   - Review Task_breakdown.md for current phase
   - Identify next incomplete task
   - Verify task dependencies are met

2. **During Development**
   - Implement one task at a time
   - Follow the 4-step completion workflow
   - Test thoroughly before committing

3. **End Session**
   - Ensure all completed tasks are tracked
   - Create session summary if significant progress made
   - Plan next session tasks

### Phase Completion Celebration 🎉
When a phase reaches 100% completion:
1. Update phase header with ✅ **COMPLETED**
2. Add completion timestamp
3. Create special commit highlighting milestone
4. Consider creating git tag: `git tag phase-X-complete`

---

## 🤖 **AI Assistant Guidelines**

When working with Claude or other AI assistants:

### Mandatory AI Behavior
- ✅ **MUST** update Task_breakdown.md after each completed task
- ✅ **MUST** commit implementation and tracking separately
- ✅ **MUST** verify task exists in breakdown before implementing
- ✅ **MUST** use conventional commit format with task references
- ✅ **MUST** follow the exact 4-step workflow process

### AI Commit Message Template
```
[type](scope): [description]

- [detailed implementation notes]
- [technical decisions made]
- [any important context]

Completes Phase X.Y.Z: [task description]
✅ Task completed from Task_breakdown.md
```

---

## 📊 **Progress Tracking Benefits**

### For Developers
- Clear visibility of completed vs. remaining work
- Historical record of development timeline
- Easy identification of current development phase
- Motivation through visible progress

### For Project Management
- Accurate progress reporting
- Time estimation for remaining work
- Identification of bottlenecks or delays
- Professional documentation trail

### For Team Coordination
- Shared understanding of project status
- Clear handoff points between team members
- Reduced duplicate work
- Better planning and scheduling

---

## 🚨 **Critical Rules**

### Never Skip These Steps
1. **Task Tracking**: Every completed task MUST be marked in Task_breakdown.md
2. **Separate Commits**: Implementation and tracking require separate commits
3. **Accurate Timestamps**: Use actual completion date, not commit date
4. **Consistent Format**: Follow exact format specifications
5. **Phase Completion**: Only mark phases complete when ALL subtasks done

### Quality Checkpoints
- Code compiles and runs without errors
- Basic functionality works as expected
- Task matches specification in Task_breakdown.md
- Commit message follows conventional format
- Task_breakdown.md is properly updated

---

*This workflow ensures professional development practices and maintains clear project progress visibility throughout the V2T development lifecycle.*
