// frontend/src/components/ActivityTimelineView.tsx
import React, { useState, useEffect } from 'react';
import {
  Clock,
  Calendar,
  User,
  Building,
  Target,
  Phone,
  Mail,
  Users,
  CheckSquare,
  FileText,
  Filter,
  Search,
  ChevronDown,
  Check,
  X,
  Play,
  Pause,
  AlertCircle,
  MessageSquare
} from 'lucide-react';
import { Activity, Task, TaskListItem, activitiesApi } from '../api/activities';

interface TimelineItem {
  id: string;
  type: 'activity' | 'task' | 'interaction';
  title: string;
  description?: string;
  timestamp: Date;
  status: string;
  priority: string;
  user: string;
  related?: {
    contact?: string;
    company?: string;
    opportunity?: string;
  };
  data: any;
  icon: React.ComponentType<any>;
  color: string;
}

interface ActivityTimelineProps {
  activities: Activity[];
  tasks: TaskListItem[];
}

const ActivityTimelineView: React.FC<ActivityTimelineProps> = ({
  activities,
  tasks
}) => {
  const [timelineItems, setTimelineItems] = useState<TimelineItem[]>([]);
  const [filteredItems, setFilteredItems] = useState<TimelineItem[]>([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [typeFilter, setTypeFilter] = useState<'all' | 'activity' | 'task' | 'interaction'>('all');
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [dateRange, setDateRange] = useState<'all' | 'today' | 'week' | 'month'>('all');
  const [showFilters, setShowFilters] = useState(false);
  const [interactions, setInteractions] = useState<any[]>([]);

  // Load interactions
  useEffect(() => {
    const loadInteractions = async () => {
      try {
        const response = await activitiesApi.getInteractionLogs();
        setInteractions(response.results || []);
      } catch (error) {
        console.error('Error loading interactions:', error);
      }
    };

    loadInteractions();
  }, []);

  // Convert data to timeline items
  useEffect(() => {
    const items: TimelineItem[] = [];

    // Add activities
    activities.forEach(activity => {
      items.push({
        id: `activity-${activity.id}`,
        type: 'activity',
        title: activity.title,
        description: activity.description,
        timestamp: new Date(activity.scheduled_at),
        status: activity.status,
        priority: activity.priority,
        user: `${activity.assigned_to?.first_name} ${activity.assigned_to?.last_name}`,
        related: {
          contact: activity.contact?.full_name,
          company: activity.company?.name,
          opportunity: activity.opportunity?.name,
        },
        data: activity,
        icon: getActivityIcon(activity.activity_type?.name),
        color: activity.activity_type?.color || '#6366f1'
      });
    });

    // Add tasks
    tasks.forEach(task => {
      items.push({
        id: `task-${task.id}`,
        type: 'task',
        title: task.title,
        description: task.description,
        timestamp: task.due_date ? new Date(task.due_date) : new Date(task.created_at),
        status: task.status,
        priority: task.priority,
        user: task.assigned_to_name || 'Unassigned',
        related: {
          contact: task.contact_name,        // Changed
          company: task.company_name,        // Changed
          opportunity: task.opportunity_name, // Changed
        },
        data: task,
        icon: CheckSquare,
        color: '#3b82f6'
      });
    });

    // Add interactions
    interactions.forEach(interaction => {
      items.push({
        id: `interaction-${interaction.id}`,
        type: 'interaction',
        title: interaction.title,
        description: interaction.notes,
        timestamp: new Date(interaction.interaction_date),
        status: 'completed',
        priority: 'medium',
        user: `${interaction.logged_by?.first_name} ${interaction.logged_by?.last_name}`,
        related: {
          contact: interaction.contact_name,
          company: interaction.company_name,
          opportunity: interaction.opportunity_name,
        },
        data: interaction,
        icon: getInteractionIcon(interaction.interaction_type),
        color: '#10b981'
      });
    });

    // Sort by timestamp (most recent first)
    items.sort((a, b) => b.timestamp.getTime() - a.timestamp.getTime());
    
    setTimelineItems(items);
  }, [activities, tasks, interactions]);

  // Apply filters
  useEffect(() => {
    let filtered = [...timelineItems];

    // Filter by search term
    if (searchTerm) {
      filtered = filtered.filter(item =>
        item.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
        item.description?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        item.user.toLowerCase().includes(searchTerm.toLowerCase()) ||
        Object.values(item.related || {}).some(val => 
          val?.toLowerCase().includes(searchTerm.toLowerCase())
        )
      );
    }

    // Filter by type
    if (typeFilter !== 'all') {
      filtered = filtered.filter(item => item.type === typeFilter);
    }

    // Filter by status
    if (statusFilter !== 'all') {
      filtered = filtered.filter(item => item.status === statusFilter);
    }

    // Filter by date range
    if (dateRange !== 'all') {
      const now = new Date();
      const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
      const weekAgo = new Date(today.getTime() - 7 * 24 * 60 * 60 * 1000);
      const monthAgo = new Date(today.getTime() - 30 * 24 * 60 * 60 * 1000);

      filtered = filtered.filter(item => {
        const itemDate = new Date(item.timestamp);
        switch (dateRange) {
          case 'today':
            return itemDate >= today;
          case 'week':
            return itemDate >= weekAgo;
          case 'month':
            return itemDate >= monthAgo;
          default:
            return true;
        }
      });
    }

    setFilteredItems(filtered);
  }, [timelineItems, searchTerm, typeFilter, statusFilter, dateRange]);

  const getActivityIcon = (typeName?: string) => {
    switch (typeName?.toLowerCase()) {
      case 'call': return Phone;
      case 'email': return Mail;
      case 'meeting': return Users;
      case 'task': return CheckSquare;
      case 'note': return FileText;
      default: return Calendar;
    }
  };

  const getInteractionIcon = (type: string) => {
    switch (type) {
      case 'call_inbound':
      case 'call_outbound':
        return Phone;
      case 'email_sent':
      case 'email_received':
        return Mail;
      case 'meeting':
        return Users;
      case 'note':
        return FileText;
      case 'sms':
        return MessageSquare;
      default:
        return Clock;
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed': return Check;
      case 'in_progress': return Play;
      case 'cancelled': return X;
      case 'overdue': return AlertCircle;
      default: return Clock;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return 'text-green-400 bg-green-500/10';
      case 'in_progress': return 'text-blue-400 bg-blue-500/10';
      case 'scheduled': return 'text-purple-400 bg-purple-500/10';
      case 'overdue': return 'text-red-400 bg-red-500/10';
      case 'cancelled': return 'text-gray-400 bg-gray-500/10';
      default: return 'text-gray-400 bg-gray-500/10';
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high': return 'text-red-400';
      case 'medium': return 'text-yellow-400';
      case 'low': return 'text-green-400';
      default: return 'text-gray-400';
    }
  };

  const formatTimestamp = (timestamp: Date) => {
    const now = new Date();
    const diffMs = now.getTime() - timestamp.getTime();
    const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));
    const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
    const diffMinutes = Math.floor(diffMs / (1000 * 60));

    if (diffDays > 7) {
      return timestamp.toLocaleDateString();
    } else if (diffDays > 0) {
      return `${diffDays} day${diffDays > 1 ? 's' : ''} ago`;
    } else if (diffHours > 0) {
      return `${diffHours} hour${diffHours > 1 ? 's' : ''} ago`;
    } else if (diffMinutes > 0) {
      return `${diffMinutes} minute${diffMinutes > 1 ? 's' : ''} ago`;
    } else {
      return 'Just now';
    }
  };

  const groupItemsByDate = (items: TimelineItem[]) => {
    const groups: { [key: string]: TimelineItem[] } = {};
    
    items.forEach(item => {
      const dateKey = item.timestamp.toDateString();
      if (!groups[dateKey]) {
        groups[dateKey] = [];
      }
      groups[dateKey].push(item);
    });

    return Object.entries(groups).sort(([a], [b]) => 
      new Date(b).getTime() - new Date(a).getTime()
    );
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-white">Activity Timeline</h2>
          <p className="text-gray-400">Chronological view of all activities, tasks, and interactions</p>
        </div>
        <button
          onClick={() => setShowFilters(!showFilters)}
          className="flex items-center space-x-2 px-4 py-2 bg-slate-700/50 text-gray-300 rounded-lg hover:bg-slate-600/50 transition-colors"
        >
          <Filter className="h-4 w-4" />
          <span>Filters</span>
          <ChevronDown className={`h-4 w-4 transition-transform ${showFilters ? 'rotate-180' : ''}`} />
        </button>
      </div>

      {/* Filters Panel */}
      {showFilters && (
        <div className="bg-gradient-to-r from-slate-800/50 to-slate-700/50 backdrop-blur-xl border border-orange-500/20 rounded-2xl p-6">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
            {/* Search */}
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
              <input
                type="text"
                placeholder="Search timeline..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-4 py-2 bg-slate-700/50 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-orange-500"
              />
            </div>

            {/* Type Filter */}
            <select
              value={typeFilter}
              onChange={(e) => setTypeFilter(e.target.value as any)}
              className="w-full px-4 py-2 bg-slate-700/50 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-orange-500"
            >
              <option value="all">All Types</option>
              <option value="activity">Activities</option>
              <option value="task">Tasks</option>
              <option value="interaction">Interactions</option>
            </select>

            {/* Status Filter */}
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="w-full px-4 py-2 bg-slate-700/50 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-orange-500"
            >
              <option value="all">All Status</option>
              <option value="scheduled">Scheduled</option>
              <option value="in_progress">In Progress</option>
              <option value="completed">Completed</option>
              <option value="overdue">Overdue</option>
              <option value="cancelled">Cancelled</option>
            </select>

            {/* Date Range */}
            <select
              value={dateRange}
              onChange={(e) => setDateRange(e.target.value as any)}
              className="w-full px-4 py-2 bg-slate-700/50 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-orange-500"
            >
              <option value="all">All Time</option>
              <option value="today">Today</option>
              <option value="week">Last 7 Days</option>
              <option value="month">Last 30 Days</option>
            </select>

            {/* Clear Filters */}
            <button
              onClick={() => {
                setSearchTerm('');
                setTypeFilter('all');
                setStatusFilter('all');
                setDateRange('all');
              }}
              className="px-4 py-2 bg-slate-600/50 text-gray-300 rounded-lg hover:bg-slate-600 transition-colors flex items-center justify-center"
            >
              <X className="h-4 w-4 mr-2" />
              Clear
            </button>
          </div>
        </div>
      )}

      {/* Timeline Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-gradient-to-r from-blue-500/20 to-cyan-500/20 border border-blue-500/30 rounded-xl p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-blue-300 text-sm">Total Items</p>
              <p className="text-white text-2xl font-bold">{filteredItems.length}</p>
            </div>
            <Clock className="h-8 w-8 text-blue-400" />
          </div>
        </div>
        <div className="bg-gradient-to-r from-green-500/20 to-emerald-500/20 border border-green-500/30 rounded-xl p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-green-300 text-sm">Completed</p>
              <p className="text-white text-2xl font-bold">
                {filteredItems.filter(item => item.status === 'completed').length}
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
                {filteredItems.filter(item => item.status === 'in_progress').length}
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
                {filteredItems.filter(item => item.status === 'overdue').length}
              </p>
            </div>
            <AlertCircle className="h-8 w-8 text-red-400" />
          </div>
        </div>
      </div>

      {/* Timeline */}
      <div className="bg-gradient-to-r from-slate-800/50 to-slate-700/50 backdrop-blur-xl border border-orange-500/20 rounded-2xl">
        {filteredItems.length === 0 ? (
          <div className="text-center py-12">
            <Clock className="h-16 w-16 text-gray-400 mx-auto mb-4" />
            <h3 className="text-xl font-medium text-white mb-2">No Timeline Items Found</h3>
            <p className="text-gray-400">Try adjusting your filters or create some activities.</p>
          </div>
        ) : (
          <div className="p-6">
            {groupItemsByDate(filteredItems).map(([dateString, dayItems]) => (
              <div key={dateString} className="mb-8 last:mb-0">
                {/* Date Header */}
                <div className="flex items-center mb-6">
                  <div className="bg-orange-500/20 text-orange-300 px-3 py-1 rounded-full text-sm font-medium">
                    {new Date(dateString).toLocaleDateString('en-US', {
                      weekday: 'long',
                      month: 'long',
                      day: 'numeric'
                    })}
                  </div>
                  <div className="flex-1 h-px bg-gradient-to-r from-orange-500/30 to-transparent ml-4"></div>
                </div>

                {/* Timeline Items for this date */}
                <div className="space-y-6">
                  {dayItems.map((item, index) => {
                    const Icon = item.icon;
                    const StatusIcon = getStatusIcon(item.status);
                    
                    return (
                      <div key={item.id} className="flex space-x-4">
                        {/* Timeline connector */}
                        <div className="flex flex-col items-center">
                          <div 
                            className="p-2 rounded-full border-2 border-gray-600 bg-slate-800"
                            style={{ borderColor: `${item.color}40` }}
                          >
                            <Icon 
                              className="h-4 w-4" 
                              style={{ color: item.color }}
                            />
                          </div>
                          {index < dayItems.length - 1 && (
                            <div className="w-px h-16 bg-gradient-to-b from-gray-600 to-transparent mt-2"></div>
                          )}
                        </div>

                        {/* Content */}
                        <div className="flex-1 bg-slate-700/30 rounded-lg p-4 border border-gray-600/50">
                          <div className="flex items-start justify-between mb-3">
                            <div>
                              <h3 className="text-white font-medium">{item.title}</h3>
                              {item.description && (
                                <p className="text-gray-400 text-sm mt-1 line-clamp-2">
                                  {item.description}
                                </p>
                              )}
                            </div>
                            <div className="flex items-center space-x-2">
                              <span className={`px-2 py-1 rounded text-xs ${getStatusColor(item.status)}`}>
                                <StatusIcon className="h-3 w-3 inline mr-1" />
                                {item.status.replace('_', ' ')}
                              </span>
                              <span className={`text-xs font-medium ${getPriorityColor(item.priority)}`}>
                                {item.priority.toUpperCase()}
                              </span>
                            </div>
                          </div>

                          <div className="flex items-center justify-between text-sm">
                            <div className="flex items-center space-x-4 text-gray-400">
                              <div className="flex items-center space-x-1">
                                <User className="h-3 w-3" />
                                <span>{item.user}</span>
                              </div>
                              <div className="flex items-center space-x-1">
                                <Clock className="h-3 w-3" />
                                <span>{formatTimestamp(item.timestamp)}</span>
                              </div>
                              <span className="capitalize px-2 py-1 bg-slate-600/50 rounded text-xs">
                                {item.type}
                              </span>
                            </div>
                          </div>

                          {/* Related Items */}
                          {(item.related?.contact || item.related?.company || item.related?.opportunity) && (
                            <div className="mt-3 pt-3 border-t border-gray-600/30">
                              <div className="flex flex-wrap gap-2 text-xs">
                                {item.related.contact && (
                                  <div className="flex items-center space-x-1 text-gray-400 bg-slate-600/30 px-2 py-1 rounded">
                                    <User className="h-3 w-3" />
                                    <span>{item.related.contact}</span>
                                  </div>
                                )}
                                {item.related.company && (
                                  <div className="flex items-center space-x-1 text-gray-400 bg-slate-600/30 px-2 py-1 rounded">
                                    <Building className="h-3 w-3" />
                                    <span>{item.related.company}</span>
                                  </div>
                                )}
                                {item.related.opportunity && (
                                  <div className="flex items-center space-x-1 text-gray-400 bg-slate-600/30 px-2 py-1 rounded">
                                    <Target className="h-3 w-3" />
                                    <span>{item.related.opportunity}</span>
                                  </div>
                                )}
                              </div>
                            </div>
                          )}
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default ActivityTimelineView;