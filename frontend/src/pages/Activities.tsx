// frontend/src/pages/Activities.tsx
import React, { useState, useEffect } from 'react';
import {
  Calendar,
  Clock,
  Plus,
  Filter,
  Search,
  Phone,
  Mail,
  Users,
  CheckSquare,
  FileText,
  AlertCircle,
  MoreHorizontal,
  Check,
  X,
  Play,
  Pause,
  User,
  Building,
  Target,
  Bell,
  BellOff,
} from 'lucide-react';
import { activitiesApi, Activity, Task, ActivityType, TaskListItem } from '../api/activities';
import { contactsApi } from '../api/contacts';
import { pipelineApi } from '../api/pipeline';
import { getUsers } from '../api/users';
import { useAuth } from '../contexts/AuthContext';
import ActivityModal from '../components/ActivityModal';
import TaskModal from '../components/TaskModal';
import ActivityTimelineView from '../components/ActivityTimelineView';
import CalendarIntegration from '../components/CalendarIntegration';

interface User {
  id: number;
  first_name: string;
  last_name: string;
  full_name?: string;
}

interface Contact {
  id: number;
  first_name: string;
  last_name: string;
  full_name?: string;
}

interface Company {
  id: number;
  name: string;
}

interface Opportunity {
  id: number;
  name: string;
}

const Activities: React.FC = () => {
  const { user } = useAuth();
  const [activities, setActivities] = useState<Activity[]>([]);
  const [tasks, setTasks] = useState<TaskListItem[]>([]);
  const [activityTypes, setActivityTypes] = useState<ActivityType[]>([]);
  const [users, setUsers] = useState<User[]>([]);
  const [contacts, setContacts] = useState<Contact[]>([]);
  const [companies, setCompanies] = useState<Company[]>([]);
  const [opportunities, setOpportunities] = useState<Opportunity[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // UI State
  const [activeTab, setActiveTab] = useState<'activities' | 'tasks' | 'calendar' | 'timeline'>('activities');
  const [showActivityModal, setShowActivityModal] = useState(false);
  const [showTaskModal, setShowTaskModal] = useState(false);
  const [selectedActivity, setSelectedActivity] = useState<Activity | null>(null);
  const [selectedTask, setSelectedTask] = useState<Task | null>(null);
  const [isCreating, setIsCreating] = useState(false);

  // Filters
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('');
  const [priorityFilter, setPriorityFilter] = useState<string>('');
  const [assigneeFilter, setAssigneeFilter] = useState<string>('');
  const [typeFilter, setTypeFilter] = useState<string>('');
  const [dateFilter, setDateFilter] = useState<string>('all'); // today, week, month, overdue, all

  useEffect(() => {
    loadData();
  }, []);

  useEffect(() => {
    applyFilters();
  }, [searchTerm, statusFilter, priorityFilter, assigneeFilter, typeFilter, dateFilter]);

  const loadData = async () => {
    try {
      setLoading(true);
      setError(null);

      const [
        activitiesRes,
        tasksRes,
        activityTypesRes,
        contactsRes,
        companiesRes,
        opportunitiesRes,
        usersData
      ] = await Promise.all([
        activitiesApi.getActivities(),
        activitiesApi.getTasks(),
        activitiesApi.getActivityTypes(),
        contactsApi.getContacts({ limit: 1000 }),
        contactsApi.getCompanies({ limit: 1000 }),
        pipelineApi.getOpportunities({ limit: 1000 }),
        getUsers()
      ]);

      setActivities(activitiesRes.results);
      setTasks(tasksRes.results);
      setActivityTypes(activityTypesRes);
      setContacts(contactsRes.results);
      setCompanies(companiesRes.results);
      setOpportunities(opportunitiesRes.results);
      setUsers(usersData.results); 

    } catch (err) {
      setError('Failed to load activities data');
      console.error('Error loading activities:', err);
    } finally {
      setLoading(false);
    }
  };

  const applyFilters = () => {
    // This would apply client-side filters or trigger API calls with filters
    // For now, we'll just reload data if needed
  };

  const handleCreateActivity = () => {
    setSelectedActivity(null);
    setIsCreating(true);
    setShowActivityModal(true);
  };

  const handleEditActivity = (activity: Activity) => {
    setSelectedActivity(activity);
    setIsCreating(false);
    setShowActivityModal(true);
  };

  const handleCreateTask = () => {
    setSelectedTask(null);
    setIsCreating(true);
    setShowTaskModal(true);
  };

  const handleEditTask = async (taskListItem: TaskListItem) => {
    try {
      const fullTask = await activitiesApi.getTask(taskListItem.id);
      setSelectedTask(fullTask);
      setIsCreating(false);
      setShowTaskModal(true);
    } catch (error) {
      console.error("Error fetching task details:", error);
    }
  };


  const handleCompleteActivity = async (activity: Activity) => {
    try {
      await activitiesApi.completeActivity(activity.id, { outcome: 'successful' });
      loadData(); // Reload to get updated data
    } catch (err) {
      console.error('Error completing activity:', err);
    }
  };

  const handleCompleteTask = async (task: TaskListItem) => {
    try {
      await activitiesApi.completeTask(task.id, {});
      loadData(); // Reload to get updated data
    } catch (err) {
      console.error('Error completing task:', err);
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high': return 'text-red-400 bg-red-500/10 border-red-500/20';
      case 'medium': return 'text-yellow-400 bg-yellow-500/10 border-yellow-500/20';
      case 'low': return 'text-green-400 bg-green-500/10 border-green-500/20';
      default: return 'text-gray-400 bg-gray-500/10 border-gray-500/20';
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return 'text-green-400 bg-green-500/10 border-green-500/20';
      case 'in_progress': return 'text-blue-400 bg-blue-500/10 border-blue-500/20';
      case 'scheduled': return 'text-purple-400 bg-purple-500/10 border-purple-500/20';
      case 'overdue': return 'text-red-400 bg-red-500/10 border-red-500/20';
      case 'cancelled': return 'text-gray-400 bg-gray-500/10 border-gray-500/20';
      default: return 'text-gray-400 bg-gray-500/10 border-gray-500/20';
    }
  };

  const getActivityIcon = (typeName: string) => {
    switch (typeName?.toLowerCase()) {
      case 'call': return Phone;
      case 'email': return Mail;
      case 'meeting': return Users;
      case 'task': return CheckSquare;
      case 'note': return FileText;
      default: return Calendar;
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-orange-500"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-white">Activities & Follow-up</h1>
          <p className="text-gray-300 mt-1">Manage tasks, schedule activities, and track interactions</p>
        </div>
        <div className="flex space-x-3">
          <button
            onClick={handleCreateTask}
            className="bg-gradient-to-r from-blue-500 to-cyan-500 text-white px-4 py-2 rounded-lg font-medium hover:shadow-lg transition-all duration-200 flex items-center space-x-2"
          >
            <Plus className="h-4 w-4" />
            <span>New Task</span>
          </button>
          <button
            onClick={handleCreateActivity}
            className="bg-gradient-to-r from-orange-500 to-pink-500 text-white px-4 py-2 rounded-lg font-medium hover:shadow-lg transition-all duration-200 flex items-center space-x-2"
          >
            <Plus className="h-4 w-4" />
            <span>New Activity</span>
          </button>
        </div>
      </div>

      {/* Tab Navigation */}
      <div className="flex space-x-1 bg-slate-800/50 p-1 rounded-lg">
        {[
          { id: 'activities', label: 'Activities', icon: Calendar },
          { id: 'tasks', label: 'Tasks', icon: CheckSquare },
          { id: 'calendar', label: 'Calendar', icon: Calendar },
          { id: 'timeline', label: 'Timeline', icon: Clock }
        ].map(tab => {
          const Icon = tab.icon;
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as any)}
              className={`flex items-center space-x-2 px-4 py-2 rounded-md text-sm font-medium transition-all ${
                activeTab === tab.id
                  ? 'bg-orange-500 text-white'
                  : 'text-gray-400 hover:text-white hover:bg-slate-700/50'
              }`}
            >
              <Icon className="h-4 w-4" />
              <span>{tab.label}</span>
            </button>
          );
        })}
      </div>

      {/* Filters */}
      {(activeTab === 'activities' || activeTab === 'tasks') && (
        <div className="bg-gradient-to-r from-slate-800/50 to-slate-700/50 backdrop-blur-xl border border-orange-500/20 rounded-2xl p-6">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-6 gap-4">
            {/* Search */}
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
              <input
                type="text"
                placeholder="Search..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-4 py-2 bg-slate-700/50 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-orange-500"
              />
            </div>

            {/* Status Filter */}
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="w-full px-4 py-2 bg-slate-700/50 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-orange-500"
            >
              <option value="">All Status</option>
              <option value="scheduled">Scheduled</option>
              <option value="in_progress">In Progress</option>
              <option value="completed">Completed</option>
              <option value="overdue">Overdue</option>
              <option value="cancelled">Cancelled</option>
            </select>

            {/* Priority Filter */}
            <select
              value={priorityFilter}
              onChange={(e) => setPriorityFilter(e.target.value)}
              className="w-full px-4 py-2 bg-slate-700/50 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-orange-500"
            >
              <option value="">All Priority</option>
              <option value="high">High</option>
              <option value="medium">Medium</option>
              <option value="low">Low</option>
            </select>

            {/* Type Filter (for activities) */}
            {activeTab === 'activities' && (
              <select
                value={typeFilter}
                onChange={(e) => setTypeFilter(e.target.value)}
                className="w-full px-4 py-2 bg-slate-700/50 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-orange-500"
              >
                <option value="">All Types</option>
                {activityTypes.map(type => (
                  <option key={type.id} value={type.id}>{type.name}</option>
                ))}
              </select>
            )}

            {/* Date Filter */}
            <select
              value={dateFilter}
              onChange={(e) => setDateFilter(e.target.value)}
              className="w-full px-4 py-2 bg-slate-700/50 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-orange-500"
            >
              <option value="all">All Time</option>
              <option value="today">Today</option>
              <option value="week">This Week</option>
              <option value="month">This Month</option>
              <option value="overdue">Overdue</option>
            </select>

            {/* Clear Filters */}
            <button
              onClick={() => {
                setSearchTerm('');
                setStatusFilter('');
                setPriorityFilter('');
                setAssigneeFilter('');
                setTypeFilter('');
                setDateFilter('all');
              }}
              className="px-4 py-2 bg-slate-600/50 text-gray-300 rounded-lg hover:bg-slate-600 transition-colors flex items-center justify-center"
            >
              <X className="h-4 w-4 mr-2" />
              Clear
            </button>
          </div>
        </div>
      )}

      {/* Content based on active tab */}
      {activeTab === 'activities' && (
        <ActivitiesTab
          activities={activities}
          activityTypes={activityTypes}
          onEdit={handleEditActivity}
          onComplete={handleCompleteActivity}
          getPriorityColor={getPriorityColor}
          getStatusColor={getStatusColor}
          getActivityIcon={getActivityIcon}
        />
      )}

      {activeTab === 'tasks' && (
        <TasksTab
          tasks={tasks}
          onEdit={handleEditTask}
          onComplete={handleCompleteTask}
          getPriorityColor={getPriorityColor}
          getStatusColor={getStatusColor}
        />
      )}

      {activeTab === 'calendar' && (
        <CalendarIntegration activities={activities} tasks={tasks} />
      )}

      {activeTab === 'timeline' && (
        <ActivityTimelineView activities={activities} tasks={tasks} />
      )}

      {/* Modals */}
      {showActivityModal && (
        <ActivityModal
          activity={selectedActivity}
          isOpen={showActivityModal}
          isCreating={isCreating}
          activityTypes={activityTypes}
          contacts={contacts}
          companies={companies}
          opportunities={opportunities}
          users={users}
          onClose={() => setShowActivityModal(false)}
          onSave={loadData}
        />
      )}

      {showTaskModal && (
        <TaskModal
          task={selectedTask}
          isOpen={showTaskModal}
          isCreating={isCreating}
          contacts={contacts}
          companies={companies}
          opportunities={opportunities}
          users={users}
          onClose={() => setShowTaskModal(false)}
          onSave={loadData}
        />
      )}
    </div>
  );
};

// Activities Tab Component
const ActivitiesTab: React.FC<{
  activities: Activity[];
  activityTypes: ActivityType[];
  onEdit: (activity: Activity) => void;
  onComplete: (activity: Activity) => void;
  getPriorityColor: (priority: string) => string;
  getStatusColor: (status: string) => string;
  getActivityIcon: (typeName: string) => React.ComponentType<any>;
}> = ({ activities, activityTypes, onEdit, onComplete, getPriorityColor, getStatusColor, getActivityIcon }) => {
  return (
    <div className="space-y-4">
      {/* Quick Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-gradient-to-r from-blue-500/20 to-cyan-500/20 border border-blue-500/30 rounded-xl p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-blue-300 text-sm">Total Activities</p>
              <p className="text-white text-2xl font-bold">{activities.length}</p>
            </div>
            <Calendar className="h-8 w-8 text-blue-400" />
          </div>
        </div>
        <div className="bg-gradient-to-r from-green-500/20 to-emerald-500/20 border border-green-500/30 rounded-xl p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-green-300 text-sm">Completed</p>
              <p className="text-white text-2xl font-bold">
                {activities.filter(a => a.status === 'completed').length}
              </p>
            </div>
            <Check className="h-8 w-8 text-green-400" />
          </div>
        </div>
        <div className="bg-gradient-to-r from-yellow-500/20 to-orange-500/20 border border-yellow-500/30 rounded-xl p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-yellow-300 text-sm">In Progress</p>
              <p className="text-white text-2xl font-bold">
                {activities.filter(a => a.status === 'in_progress').length}
              </p>
            </div>
            <Play className="h-8 w-8 text-yellow-400" />
          </div>
        </div>
        <div className="bg-gradient-to-r from-red-500/20 to-pink-500/20 border border-red-500/30 rounded-xl p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-red-300 text-sm">Overdue</p>
              <p className="text-white text-2xl font-bold">
                {activities.filter(a => a.status === 'overdue').length}
              </p>
            </div>
            <AlertCircle className="h-8 w-8 text-red-400" />
          </div>
        </div>
      </div>

      {/* Activities List */}
      <div className="bg-gradient-to-r from-slate-800/50 to-slate-700/50 backdrop-blur-xl border border-orange-500/20 rounded-2xl overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-slate-800/80">
              <tr>
                <th className="text-left p-4 text-gray-300 font-medium">Activity</th>
                <th className="text-left p-4 text-gray-300 font-medium">Type</th>
                <th className="text-left p-4 text-gray-300 font-medium">Status</th>
                <th className="text-left p-4 text-gray-300 font-medium">Priority</th>
                <th className="text-left p-4 text-gray-300 font-medium">Scheduled</th>
                <th className="text-left p-4 text-gray-300 font-medium">Assigned To</th>
                <th className="text-left p-4 text-gray-300 font-medium">Related</th>
                <th className="text-right p-4 text-gray-300 font-medium">Actions</th>
              </tr>
            </thead>
            <tbody>
              {activities.map((activity) => {
                const Icon = getActivityIcon(activity.activity_type.name);
                return (
                  <tr key={activity.id} className="border-t border-gray-700/50 hover:bg-slate-700/30 transition-colors">
                    <td className="p-4">
                      <div className="flex items-center space-x-3">
                        <div className={`p-2 rounded-lg ${getStatusColor(activity.status)}`}>
                          <Icon className="h-4 w-4" />
                        </div>
                        <div>
                          <p className="text-white font-medium">{activity.title}</p>
                          {activity.description && (
                            <p className="text-gray-400 text-sm truncate max-w-xs">
                              {activity.description}
                            </p>
                          )}
                        </div>
                      </div>
                    </td>
                    <td className="p-4">
                      <span className="px-2 py-1 bg-slate-600/50 text-gray-300 rounded text-sm">
                        {activity.activity_type.name}
                      </span>
                    </td>
                    <td className="p-4">
                      <span className={`px-2 py-1 rounded text-sm border ${getStatusColor(activity.status)}`}>
                        {activity.status.replace('_', ' ')}
                      </span>
                    </td>
                    <td className="p-4">
                      <span className={`px-2 py-1 rounded text-sm border ${getPriorityColor(activity.priority)}`}>
                        {activity.priority}
                      </span>
                    </td>
                    <td className="p-4">
                      <div className="text-white text-sm">
                        {new Date(activity.scheduled_at).toLocaleDateString()}
                      </div>
                      <div className="text-gray-400 text-xs">
                        {new Date(activity.scheduled_at).toLocaleTimeString()}
                      </div>
                    </td>
                    <td className="p-4">
                      <div className="flex items-center space-x-2">
                        <div className="h-8 w-8 bg-orange-500 rounded-full flex items-center justify-center">
                          <span className="text-white text-xs font-medium">
                            {activity.assigned_to.first_name[0]}{activity.assigned_to.last_name[0]}
                          </span>
                        </div>
                        <span className="text-white text-sm">
                          {activity.assigned_to.first_name} {activity.assigned_to.last_name}
                        </span>
                      </div>
                    </td>
                    <td className="p-4">
                      <div className="space-y-1">
                        {activity.contact && (
                          <div className="flex items-center space-x-1 text-sm text-gray-300">
                            <User className="h-3 w-3" />
                            <span>{activity.contact.full_name}</span>
                          </div>
                        )}
                        {activity.company && (
                          <div className="flex items-center space-x-1 text-sm text-gray-300">
                            <Building className="h-3 w-3" />
                            <span>{activity.company.name}</span>
                          </div>
                        )}
                        {activity.opportunity && (
                          <div className="flex items-center space-x-1 text-sm text-gray-300">
                            <Target className="h-3 w-3" />
                            <span>{activity.opportunity.name}</span>
                          </div>
                        )}
                      </div>
                    </td>
                    <td className="p-4">
                      <div className="flex items-center justify-end space-x-2">
                        {activity.status !== 'completed' && (
                          <button
                            onClick={() => onComplete(activity)}
                            className="p-2 text-green-400 hover:bg-green-500/10 rounded-lg transition-colors"
                            title="Complete Activity"
                          >
                            <Check className="h-4 w-4" />
                          </button>
                        )}
                        <button
                          onClick={() => onEdit(activity)}
                          className="p-2 text-blue-400 hover:bg-blue-500/10 rounded-lg transition-colors"
                          title="Edit Activity"
                        >
                          <MoreHorizontal className="h-4 w-4" />
                        </button>
                      </div>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
        
        {activities.length === 0 && (
          <div className="text-center py-12">
            <Calendar className="h-16 w-16 text-gray-400 mx-auto mb-4" />
            <h3 className="text-xl font-medium text-white mb-2">No Activities Found</h3>
            <p className="text-gray-400">Get started by creating your first activity.</p>
          </div>
        )}
      </div>
    </div>
  );
};

// Tasks Tab Component
const TasksTab: React.FC<{
  tasks: TaskListItem[];
  onEdit: (task: TaskListItem) => void;
  onComplete: (task: TaskListItem) => void;
  getPriorityColor: (priority: string) => string;
  getStatusColor: (status: string) => string;
}> = ({ tasks, onEdit, onComplete, getPriorityColor, getStatusColor }) => {
  return (
    <div className="space-y-4">
      {/* Quick Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-gradient-to-r from-blue-500/20 to-cyan-500/20 border border-blue-500/30 rounded-xl p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-blue-300 text-sm">Total Tasks</p>
              <p className="text-white text-2xl font-bold">{tasks.length}</p>
            </div>
            <CheckSquare className="h-8 w-8 text-blue-400" />
          </div>
        </div>
        <div className="bg-gradient-to-r from-green-500/20 to-emerald-500/20 border border-green-500/30 rounded-xl p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-green-300 text-sm">Completed</p>
              <p className="text-white text-2xl font-bold">
                {tasks.filter((t) => t.status === "completed").length}
              </p>
            </div>
            <Check className="h-8 w-8 text-green-400" />
          </div>
        </div>
        <div className="bg-gradient-to-r from-yellow-500/20 to-orange-500/20 border border-yellow-500/30 rounded-xl p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-yellow-300 text-sm">In Progress</p>
              <p className="text-white text-2xl font-bold">
                {tasks.filter((t) => t.status === "in_progress").length}
              </p>
            </div>
            <Play className="h-8 w-8 text-yellow-400" />
          </div>
        </div>
        <div className="bg-gradient-to-r from-red-500/20 to-pink-500/20 border border-red-500/30 rounded-xl p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-red-300 text-sm">Overdue</p>
              <p className="text-white text-2xl font-bold">
                {tasks.filter((t) => t.is_overdue).length}
              </p>
            </div>
            <AlertCircle className="h-8 w-8 text-red-400" />
          </div>
        </div>
      </div>

      {/* Tasks List */}
      <div className="bg-gradient-to-r from-slate-800/50 to-slate-700/50 backdrop-blur-xl border border-orange-500/20 rounded-2xl overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-slate-800/80">
              <tr>
                <th className="text-left p-4 text-gray-300 font-medium">
                  Task
                </th>
                <th className="text-left p-4 text-gray-300 font-medium">
                  Status
                </th>
                <th className="text-left p-4 text-gray-300 font-medium">
                  Priority
                </th>
                <th className="text-left p-4 text-gray-300 font-medium">
                  Due Date
                </th>
                <th className="text-left p-4 text-gray-300 font-medium">
                  Assigned To
                </th>
                <th className="text-left p-4 text-gray-300 font-medium">
                  Related
                </th>
                <th className="text-right p-4 text-gray-300 font-medium">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody>
              {tasks.map((task) => (
                <tr
                  key={task.id}
                  className="border-t border-gray-700/50 hover:bg-slate-700/30 transition-colors"
                >
                  <td className="p-4">
                    <div className="flex items-center space-x-3">
                      <div
                        className={`p-2 rounded-lg ${getStatusColor(
                          task.status
                        )}`}
                      >
                        <CheckSquare className="h-4 w-4" />
                      </div>
                      <div>
                        <p className="text-white font-medium">{task.title}</p>
                        {task.description && (
                          <p className="text-gray-400 text-sm truncate max-w-xs">
                            {task.description}
                          </p>
                        )}
                      </div>
                    </div>
                  </td>
                  <td className="p-4">
                    <span
                      className={`px-2 py-1 rounded text-sm border ${getStatusColor(
                        task.status
                      )}`}
                    >
                      {task.status.replace("_", " ")}
                    </span>
                  </td>
                  <td className="p-4">
                    <span
                      className={`px-2 py-1 rounded text-sm border ${getPriorityColor(
                        task.priority
                      )}`}
                    >
                      {task.priority}
                    </span>
                  </td>
                  <td className="p-4">
                    {task.due_date ? (
                      <div
                        className={`text-sm ${
                          task.is_overdue ? "text-red-400" : "text-white"
                        }`}
                      >
                        {new Date(task.due_date).toLocaleDateString()}
                        {task.is_overdue && (
                          <span className="block text-xs text-red-400">
                            Overdue
                          </span>
                        )}
                      </div>
                    ) : (
                      <span className="text-gray-400 text-sm">No due date</span>
                    )}
                  </td>
                  <td className="p-4">
                    {task.assigned_to_name ? (
                      <div className="flex items-center space-x-2">
                        <div className="h-8 w-8 bg-blue-500 rounded-full flex items-center justify-center">
                          <span className="text-white text-xs font-medium">
                            {task.assigned_to_name
                              .split(" ")
                              .map((name) => name[0])
                              .join("")
                              .slice(0, 2)}
                          </span>
                        </div>
                        <span className="text-white text-sm">
                          {task.assigned_to_name}
                        </span>
                      </div>
                    ) : (
                      <div className="flex items-center space-x-2">
                        <div className="h-8 w-8 bg-gray-500 rounded-full flex items-center justify-center">
                          <User className="h-4 w-4 text-gray-300" />
                        </div>
                        <span className="text-gray-400 text-sm">
                          Unassigned
                        </span>
                      </div>
                    )}
                  </td>
                  <td className="p-4">
                    <div className="space-y-1">
                      {task.contact_name && (
                        <div className="flex items-center space-x-1 text-sm text-gray-300">
                          <User className="h-3 w-3" />
                          <span>{task.contact_name}</span>
                        </div>
                      )}
                      {task.company_name && (
                        <div className="flex items-center space-x-1 text-sm text-gray-300">
                          <Building className="h-3 w-3" />
                          <span>{task.company_name}</span>
                        </div>
                      )}
                      {task.opportunity_name && (
                        <div className="flex items-center space-x-1 text-sm text-gray-300">
                          <Target className="h-3 w-3" />
                          <span>{task.opportunity_name}</span>
                        </div>
                      )}
                      {!task.contact_name &&
                        !task.company_name &&
                        !task.opportunity_name && (
                          <div className="text-sm text-gray-500">
                            <span>No relations</span>
                          </div>
                        )}
                    </div>
                  </td>
                  <td className="p-4">
                    <div className="flex items-center justify-end space-x-2">
                      {task.status !== "completed" && (
                        <button
                          onClick={() => onComplete(task)}
                          className="p-2 text-green-400 hover:bg-green-500/10 rounded-lg transition-colors"
                          title="Complete Task"
                        >
                          <Check className="h-4 w-4" />
                        </button>
                      )}
                      <button
                        onClick={() => onEdit(task)}
                        className="p-2 text-blue-400 hover:bg-blue-500/10 rounded-lg transition-colors"
                        title="Edit Task"
                      >
                        <MoreHorizontal className="h-4 w-4" />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {tasks.length === 0 && (
          <div className="text-center py-12">
            <CheckSquare className="h-16 w-16 text-gray-400 mx-auto mb-4" />
            <h3 className="text-xl font-medium text-white mb-2">
              No Tasks Found
            </h3>
            <p className="text-gray-400">
              Create your first task to get started.
            </p>
          </div>
        )}
      </div>
    </div>
  );
};

export default Activities;