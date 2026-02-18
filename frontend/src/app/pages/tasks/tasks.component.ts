import { Component, signal, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { DragDropModule, CdkDragDrop } from '@angular/cdk/drag-drop';

interface Task {
  id: string;
  title: string;
  description: string | null;
  status: 'pending' | 'in_progress' | 'completed' | 'failed';
  task_type: 'one_time' | 'daily' | 'monthly';
  scheduled_time: string | null;
  scheduled_date: string | null;
  recurrence: 'one_time' | 'daily' | 'monthly';
  next_run_at: string | null;
  created_at: string;
  updated_at: string;
}

interface TaskForm {
  title: string;
  description: string;
  task_type: string;
  scheduled_time: string;
  scheduled_date: string;
  recurrence: string;
}

@Component({
  selector: 'app-tasks',
  standalone: true,
  imports: [CommonModule, FormsModule, DragDropModule],
  templateUrl: './tasks.component.html',
  styleUrl: './tasks.component.css',
})
export class TasksComponent implements OnInit {
  tasks = signal<Task[]>([]);
  filteredTasks = signal<Task[]>([]);
  loading = signal(false);

  showCreateModal = signal(false);
  showEditModal = signal(false);
  showDeleteConfirm = signal(false);

  activeFilter = signal<string>('all');
  searchQuery = signal('');
  viewMode = signal<'list' | 'board'>('list');

  editingTask: Task | null = null;
  deletingTask: Task | null = null;

  taskForm: TaskForm = {
    title: '',
    description: '',
    task_type: 'one_time',
    scheduled_time: '',
    scheduled_date: '',
    recurrence: 'one_time',
  };

  statusOptions = [
    { value: 'pending', label: 'Pending', color: 'amber', icon: 'schedule' },
    { value: 'in_progress', label: 'In Progress', color: 'blue', icon: 'play_circle' },
    { value: 'completed', label: 'Completed', color: 'emerald', icon: 'check_circle' },
    { value: 'failed', label: 'Failed', color: 'rose', icon: 'error' },
  ];

  typeOptions = [
    { value: 'one_time', label: 'One Time', icon: 'event' },
    { value: 'daily', label: 'Daily', icon: 'repeat' },
    { value: 'monthly', label: 'Monthly', icon: 'calendar_month' },
  ];

  filterOptions = [
    { value: 'all', label: 'All Tasks' },
    { value: 'pending', label: 'Pending' },
    { value: 'in_progress', label: 'In Progress' },
    { value: 'completed', label: 'Completed' },
    { value: 'failed', label: 'Failed' },
  ];

  ngOnInit(): void {
    this.loadTasks();
  }

  async loadTasks(): Promise<void> {
    this.loading.set(true);
    try {
      const res = await fetch('/api/tasks');
      if (res.ok) {
        const data = await res.json();
        this.tasks.set(data);
        this.applyFilter();
      }
    } catch { /* ignore */ }
    this.loading.set(false);
  }

  applyFilter(): void {
    let result = [...this.tasks()];
    const filter = this.activeFilter();
    if (filter !== 'all') {
      result = result.filter(t => t.status === filter);
    }
    const query = this.searchQuery().toLowerCase().trim();
    if (query) {
      result = result.filter(t =>
        t.title.toLowerCase().includes(query) ||
        (t.description && t.description.toLowerCase().includes(query))
      );
    }
    this.filteredTasks.set(result);
  }

  getTasksByStatus(status: string): Task[] {
    return this.filteredTasks().filter(t => t.status === status);
  }

  setFilter(filter: string): void {
    this.activeFilter.set(filter);
    this.applyFilter();
  }

  onSearchChange(): void {
    this.applyFilter();
  }

  // --- Stats ---
  getStatCount(status: string): number {
    if (status === 'all') return this.tasks().length;
    return this.tasks().filter(t => t.status === status).length;
  }

  // --- Create ---
  openCreateModal(): void {
    this.taskForm = {
      title: '',
      description: '',
      task_type: 'one_time',
      scheduled_time: '',
      scheduled_date: '',
      recurrence: 'one_time',
    };
    this.showCreateModal.set(true);
  }

  onTaskTypeChange(): void {
    this.taskForm.recurrence = this.taskForm.task_type;
    if (this.taskForm.task_type === 'daily') {
      this.taskForm.scheduled_date = '';
    }
  }

  async createTask(): Promise<void> {
    if (!this.taskForm.title.trim()) return;
    try {
      const body: any = {
        title: this.taskForm.title,
        description: this.taskForm.description || null,
        task_type: this.taskForm.task_type,
        recurrence: this.taskForm.recurrence,
        scheduled_time: this.taskForm.scheduled_time || null,
        scheduled_date: this.taskForm.scheduled_date || null,
      };
      const res = await fetch('/api/tasks', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
      });
      if (res.ok) {
        this.showCreateModal.set(false);
        this.loadTasks();
      }
    } catch { /* ignore */ }
  }

  // --- Edit ---
  openEditModal(task: Task): void {
    this.editingTask = { ...task };
    this.taskForm = {
      title: task.title,
      description: task.description || '',
      task_type: task.task_type || 'one_time',
      scheduled_time: task.scheduled_time || '',
      scheduled_date: task.scheduled_date || '',
      recurrence: task.recurrence || 'one_time',
    };
    this.showEditModal.set(true);
  }

  async updateTask(): Promise<void> {
    if (!this.editingTask || !this.taskForm.title.trim()) return;
    try {
      const body: any = {
        title: this.taskForm.title,
        description: this.taskForm.description || null,
        task_type: this.taskForm.task_type,
        recurrence: this.taskForm.recurrence,
        scheduled_time: this.taskForm.scheduled_time || null,
        scheduled_date: this.taskForm.scheduled_date || null,
      };
      const res = await fetch(`/api/tasks/${this.editingTask.id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
      });
      if (res.ok) {
        this.showEditModal.set(false);
        this.editingTask = null;
        this.loadTasks();
      }
    } catch { /* ignore */ }
  }

  // --- Status Change ---
  async changeStatus(task: Task, newStatus: string): Promise<void> {
    try {
      const res = await fetch(`/api/tasks/${task.id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ status: newStatus }),
      });
      if (res.ok) {
        this.loadTasks();
      }
    } catch { /* ignore */ }
  }

  onTaskDrop(event: CdkDragDrop<Task[]>): void {
    if (event.previousContainer === event.container) {
      return;
    }

    const task = event.item.data as Task;
    const newStatus = event.container.id as any;

    // Optimistic update
    const currentTasks = this.tasks();
    const updatedTasks = currentTasks.map(t =>
      t.id === task.id ? { ...t, status: newStatus } : t
    );
    this.tasks.set(updatedTasks);
    this.applyFilter();

    // Persist to server
    this.changeStatus(task, newStatus);
  }

  // --- Delete ---
  openDeleteConfirm(task: Task): void {
    this.deletingTask = task;
    this.showDeleteConfirm.set(true);
  }

  async confirmDelete(): Promise<void> {
    if (!this.deletingTask) return;
    try {
      const res = await fetch(`/api/tasks/${this.deletingTask.id}`, { method: 'DELETE' });
      if (res.ok) {
        this.showDeleteConfirm.set(false);
        this.deletingTask = null;
        this.loadTasks();
      }
    } catch { /* ignore */ }
  }

  // --- Helpers ---
  getStatusConfig(status: string) {
    return this.statusOptions.find(s => s.value === status) || this.statusOptions[0];
  }

  getTypeConfig(type: string) {
    return this.typeOptions.find(t => t.value === type) || this.typeOptions[0];
  }

  getRecurrenceLabel(recurrence: string): string {
    switch (recurrence) {
      case 'daily': return 'Every day';
      case 'monthly': return 'Every month';
      default: return 'One time';
    }
  }

  formatTime(time: string | null): string {
    if (!time) return '';
    try {
      const [hours, minutes] = time.split(':').map(Number);
      const period = hours >= 12 ? 'PM' : 'AM';
      const displayHours = hours % 12 || 12;
      return `${displayHours}:${minutes.toString().padStart(2, '0')} ${period}`;
    } catch {
      return time;
    }
  }

  formatDate(d: string | null): string {
    if (!d) return '';
    try {
      return new Date(d).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
      });
    } catch {
      return '';
    }
  }

  formatDateTime(d: string | null): string {
    if (!d) return '';
    try {
      return new Date(d).toLocaleString('en-US', {
        month: 'short',
        day: 'numeric',
        hour: 'numeric',
        minute: '2-digit',
        hour12: true,
      });
    } catch {
      return '';
    }
  }

  closeModals(): void {
    this.showCreateModal.set(false);
    this.showEditModal.set(false);
    this.showDeleteConfirm.set(false);
    this.editingTask = null;
    this.deletingTask = null;
  }
}
