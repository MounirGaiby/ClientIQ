// frontend/src/components/CalendarIntegration.tsx
import React, { useState, useEffect } from 'react';
import {
  Calendar,
  ChevronLeft,
  ChevronRight,
  Plus,
  Clock,
  User,
  Building,
  Target,
  Phone,
  Mail,
  Users,
  CheckSquare,
  FileText,
  Filter,
  Eye,
  MoreHorizontal,
  X
} from 'lucide-react';
import { Activity, Task } from '../api/activities';

interface CalendarIntegrationProps {
  activities: Activity[];
  tasks: Task[];
}

interface CalendarEvent {
  id: string;
  title: string;
  type: 'activity' | 'task';
  start: Date;
  end?: Date;
  priority: 'low' | 'medium' | 'high';
  status: string;
  related?: {
    contact?: string;
    company?: string;
    opportunity?: string;
  };
  data: Activity | Task;
}

const CalendarIntegration: React.FC<CalendarIntegrationProps> = ({
  activities,
  tasks
}) => {
  const [currentDate, setCurrentDate] = useState(new Date());
  const [view, setView] = useState<'month' | 'week' | 'day'>('month');
  const [selectedEvent, setSelectedEvent] = useState<CalendarEvent | null>(null);
  const [showEventDetails, setShowEventDetails] = useState(false);
  const [filterType, setFilterType] = useState<'all' | 'activities' | 'tasks'>('all');
  const [events, setEvents] = useState<CalendarEvent[]>([]);

  // Convert activities and tasks to calendar events
  useEffect(() => {
    const calendarEvents: CalendarEvent[] = [];

    // Add activities
    activities.forEach(activity => {
      const start = new Date(activity.scheduled_at);
      const end = activity.duration_minutes 
        ? new Date(start.getTime() + activity.duration_minutes * 60000)
        : new Date(start.getTime() + 60 * 60000); // Default 1 hour

      calendarEvents.push({
        id: `activity-${activity.id}`,
        title: activity.title,
        type: 'activity',
        start,
        end,
        priority: activity.priority,
        status: activity.status,
        related: {
          contact: activity.contact?.full_name,
          company: activity.company?.name,
          opportunity: activity.opportunity?.name,
        },
        data: activity
      });
    });

    // Add tasks (only those with due dates)
    tasks.forEach(task => {
      if (task.due_date) {
        const start = new Date(task.due_date);
        start.setHours(23, 59, 0, 0); // End of day for tasks

        calendarEvents.push({
          id: `task-${task.id}`,
          title: task.title,
          type: 'task',
          start,
          priority: task.priority,
          status: task.status,
          related: {
            contact: task.contact ? `${task.contact.first_name} ${task.contact.last_name}` : undefined,
            company: task.company?.name,
            opportunity: task.opportunity?.name,
          },
          data: task
        });
      }
    });

    setEvents(calendarEvents);
  }, [activities, tasks]);

  // Filter events based on selected filter
  const filteredEvents = events.filter(event => {
    if (filterType === 'all') return true;
    return event.type === filterType.slice(0, -1); // Remove 's' from 'activities'/'tasks'
  });

  const getMonthDays = () => {
    const year = currentDate.getFullYear();
    const month = currentDate.getMonth();
    
    const firstDay = new Date(year, month, 1);
    const lastDay = new Date(year, month + 1, 0);
    const daysInMonth = lastDay.getDate();
    const startingDayOfWeek = firstDay.getDay();
    
    const days = [];
    
    // Previous month days
    const prevMonth = new Date(year, month - 1, 0);
    const prevMonthDays = prevMonth.getDate();
    for (let i = startingDayOfWeek - 1; i >= 0; i--) {
      days.push({
        date: prevMonthDays - i,
        isCurrentMonth: false,
        fullDate: new Date(year, month - 1, prevMonthDays - i)
      });
    }
    
    // Current month days
    for (let day = 1; day <= daysInMonth; day++) {
      days.push({
        date: day,
        isCurrentMonth: true,
        fullDate: new Date(year, month, day)
      });
    }
    
    // Next month days
    const totalCells = 42; // 6 rows × 7 days
    const remainingCells = totalCells - days.length;
    for (let day = 1; day <= remainingCells; day++) {
      days.push({
        date: day,
        isCurrentMonth: false,
        fullDate: new Date(year, month + 1, day)
      });
    }
    
    return days;
  };

  const getEventsForDate = (date: Date) => {
    return filteredEvents.filter(event => {
      const eventDate = new Date(event.start);
      return (
        eventDate.getDate() === date.getDate() &&
        eventDate.getMonth() === date.getMonth() &&
        eventDate.getFullYear() === date.getFullYear()
      );
    });
  };

  const navigateMonth = (direction: 'prev' | 'next') => {
    const newDate = new Date(currentDate);
    newDate.setMonth(currentDate.getMonth() + (direction === 'next' ? 1 : -1));
    setCurrentDate(newDate);
  };

  const goToToday = () => {
    setCurrentDate(new Date());
  };

  const getEventIcon = (event: CalendarEvent) => {
    if (event.type === 'task') return CheckSquare;
    
    const activity = event.data as Activity;
    switch (activity.activity_type?.name?.toLowerCase()) {
      case 'call': return Phone;
      case 'email': return Mail;
      case 'meeting': return Users;
      case 'note': return FileText;
      default: return Calendar;
    }
  };

  const getEventColor = (event: CalendarEvent) => {
    if (event.type === 'task') {
      switch (event.priority) {
        case 'high': return 'bg-red-500/20 border-red-500/40 text-red-300';
        case 'medium': return 'bg-yellow-500/20 border-yellow-500/40 text-yellow-300';
        case 'low': return 'bg-green-500/20 border-green-500/40 text-green-300';
        default: return 'bg-gray-500/20 border-gray-500/40 text-gray-300';
      }
    } else {
      const activity = event.data as Activity;
      const color = activity.activity_type?.color || '#6366f1';
      return `border-[${color}]/40 text-white`;
    }
  };

  const formatTime = (date: Date) => {
    return date.toLocaleTimeString('en-US', {
      hour: 'numeric',
      minute: '2-digit',
      hour12: true
    });
  };

  const handleEventClick = (event: CalendarEvent) => {
    setSelectedEvent(event);
    setShowEventDetails(true);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <h2 className="text-2xl font-bold text-white">Calendar View</h2>
          <div className="flex items-center space-x-2">
            <button
              onClick={() => setView('month')}
              className={`px-3 py-1 rounded-md text-sm font-medium transition-colors ${
                view === 'month'
                  ? 'bg-orange-500 text-white'
                  : 'text-gray-400 hover:text-white hover:bg-slate-700/50'
              }`}
            >
              Month
            </button>
            <button
              onClick={() => setView('week')}
              className={`px-3 py-1 rounded-md text-sm font-medium transition-colors ${
                view === 'week'
                  ? 'bg-orange-500 text-white'
                  : 'text-gray-400 hover:text-white hover:bg-slate-700/50'
              }`}
            >
              Week
            </button>
            <button
              onClick={() => setView('day')}
              className={`px-3 py-1 rounded-md text-sm font-medium transition-colors ${
                view === 'day'
                  ? 'bg-orange-500 text-white'
                  : 'text-gray-400 hover:text-white hover:bg-slate-700/50'
              }`}
            >
              Day
            </button>
          </div>
        </div>
        <div className="flex items-center space-x-3">
          <select
            value={filterType}
            onChange={(e) => setFilterType(e.target.value as any)}
            className="px-3 py-2 bg-slate-700/50 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-orange-500"
          >
            <option value="all">All Events</option>
            <option value="activities">Activities Only</option>
            <option value="tasks">Tasks Only</option>
          </select>
          <button
            onClick={goToToday}
            className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors"
          >
            Today
          </button>
        </div>
      </div>

      {/* Calendar Navigation */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <button
            onClick={() => navigateMonth('prev')}
            className="p-2 text-gray-400 hover:text-white hover:bg-slate-700/50 rounded-lg transition-colors"
          >
            <ChevronLeft className="h-5 w-5" />
          </button>
          <h3 className="text-xl font-semibold text-white">
            {currentDate.toLocaleDateString('en-US', { 
              month: 'long', 
              year: 'numeric' 
            })}
          </h3>
          <button
            onClick={() => navigateMonth('next')}
            className="p-2 text-gray-400 hover:text-white hover:bg-slate-700/50 rounded-lg transition-colors"
          >
            <ChevronRight className="h-5 w-5" />
          </button>
        </div>
        <div className="flex items-center space-x-4 text-sm text-gray-400">
          <div className="flex items-center space-x-2">
            <div className="w-3 h-3 bg-orange-500/30 border border-orange-500/50 rounded"></div>
            <span>Activities</span>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-3 h-3 bg-blue-500/30 border border-blue-500/50 rounded"></div>
            <span>Tasks</span>
          </div>
        </div>
      </div>

      {/* Calendar Grid */}
      <div className="bg-gradient-to-r from-slate-800/50 to-slate-700/50 backdrop-blur-xl border border-orange-500/20 rounded-2xl overflow-hidden">
        {/* Days of Week Header */}
        <div className="grid grid-cols-7 bg-slate-800/80">
          {['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'].map(day => (
            <div key={day} className="p-4 text-center text-gray-300 font-medium border-r border-gray-700/50 last:border-r-0">
              {day}
            </div>
          ))}
        </div>

        {/* Calendar Days */}
        <div className="grid grid-cols-7">
          {getMonthDays().map((day, index) => {
            const dayEvents = getEventsForDate(day.fullDate);
            const isToday = 
              day.fullDate.getDate() === new Date().getDate() &&
              day.fullDate.getMonth() === new Date().getMonth() &&
              day.fullDate.getFullYear() === new Date().getFullYear();

            return (
              <div
                key={index}
                className={`min-h-[120px] p-2 border-r border-b border-gray-700/50 last:border-r-0 ${
                  !day.isCurrentMonth ? 'bg-slate-800/30 text-gray-500' : 'text-white'
                } ${isToday ? 'bg-orange-500/10 border-orange-500/30' : ''}`}
              >
                <div className={`text-sm font-medium mb-2 ${
                  isToday ? 'text-orange-400' : day.isCurrentMonth ? 'text-white' : 'text-gray-500'
                }`}>
                  {day.date}
                </div>
                
                {/* Events for this day */}
                <div className="space-y-1">
                  {dayEvents.slice(0, 3).map(event => {
                    const Icon = getEventIcon(event);
                    return (
                      <div
                        key={event.id}
                        onClick={() => handleEventClick(event)}
                        className={`p-1 rounded text-xs cursor-pointer border transition-colors hover:bg-opacity-80 ${getEventColor(event)}`}
                      >
                        <div className="flex items-center space-x-1">
                          <Icon className="h-3 w-3 flex-shrink-0" />
                          <span className="truncate">{event.title}</span>
                        </div>
                        {event.type === 'activity' && event.start && (
                          <div className="text-xs opacity-70 mt-1">
                            {formatTime(event.start)}
                          </div>
                        )}
                      </div>
                    );
                  })}
                  
                  {dayEvents.length > 3 && (
                    <div className="text-xs text-gray-400 text-center py-1">
                      +{dayEvents.length - 3} more
                    </div>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Event Details Modal */}
      {showEventDetails && selectedEvent && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4">
          <div className="bg-gradient-to-br from-slate-900 to-slate-800 border border-orange-500/20 rounded-2xl w-full max-w-md">
            {/* Header */}
            <div className="flex items-center justify-between p-4 border-b border-gray-700/50">
              <div className="flex items-center space-x-3">
                <div className={`p-2 rounded-lg ${
                  selectedEvent.type === 'activity' ? 'bg-orange-500/20' : 'bg-blue-500/20'
                }`}>
                  {React.createElement(getEventIcon(selectedEvent), {
                    className: `h-5 w-5 ${
                      selectedEvent.type === 'activity' ? 'text-orange-400' : 'text-blue-400'
                    }`
                  })}
                </div>
                <div>
                  <h3 className="text-lg font-semibold text-white">
                    {selectedEvent.title}
                  </h3>
                  <p className="text-sm text-gray-400 capitalize">
                    {selectedEvent.type}
                  </p>
                </div>
              </div>
              <button
                onClick={() => setShowEventDetails(false)}
                className="p-2 text-gray-400 hover:text-white hover:bg-white/10 rounded-lg transition-colors"
              >
                <X className="h-5 w-5" />
              </button>
            </div>

            {/* Content */}
            <div className="p-4 space-y-4">
              {/* Time */}
              <div className="flex items-center space-x-3">
                <Clock className="h-4 w-4 text-gray-400" />
                <div>
                  <p className="text-white">
                    {selectedEvent.start.toLocaleDateString('en-US', {
                      weekday: 'long',
                      year: 'numeric',
                      month: 'long',
                      day: 'numeric'
                    })}
                  </p>
                  {selectedEvent.type === 'activity' && (
                    <p className="text-gray-400 text-sm">
                      {formatTime(selectedEvent.start)}
                      {selectedEvent.end && ` - ${formatTime(selectedEvent.end)}`}
                    </p>
                  )}
                </div>
              </div>

              {/* Status & Priority */}
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <span className="text-gray-400 text-sm">Status:</span>
                  <span className={`px-2 py-1 rounded text-xs ${
                    selectedEvent.status === 'completed' ? 'bg-green-500/20 text-green-300' :
                    selectedEvent.status === 'overdue' ? 'bg-red-500/20 text-red-300' :
                    'bg-blue-500/20 text-blue-300'
                  }`}>
                    {selectedEvent.status.replace('_', ' ')}
                  </span>
                </div>
                <div className="flex items-center space-x-2">
                  <span className="text-gray-400 text-sm">Priority:</span>
                  <span className={`px-2 py-1 rounded text-xs ${
                    selectedEvent.priority === 'high' ? 'bg-red-500/20 text-red-300' :
                    selectedEvent.priority === 'medium' ? 'bg-yellow-500/20 text-yellow-300' :
                    'bg-green-500/20 text-green-300'
                  }`}>
                    {selectedEvent.priority}
                  </span>
                </div>
              </div>

              {/* Related Items */}
              {(selectedEvent.related?.contact || selectedEvent.related?.company || selectedEvent.related?.opportunity) && (
                <div className="space-y-2">
                  <h4 className="text-sm font-medium text-gray-300">Related:</h4>
                  {selectedEvent.related.contact && (
                    <div className="flex items-center space-x-2 text-sm text-gray-400">
                      <User className="h-3 w-3" />
                      <span>{selectedEvent.related.contact}</span>
                    </div>
                  )}
                  {selectedEvent.related.company && (
                    <div className="flex items-center space-x-2 text-sm text-gray-400">
                      <Building className="h-3 w-3" />
                      <span>{selectedEvent.related.company}</span>
                    </div>
                  )}
                  {selectedEvent.related.opportunity && (
                    <div className="flex items-center space-x-2 text-sm text-gray-400">
                      <Target className="h-3 w-3" />
                      <span>{selectedEvent.related.opportunity}</span>
                    </div>
                  )}
                </div>
              )}

              {/* Description */}
              {'description' in selectedEvent.data && selectedEvent.data.description && (
                <div className="space-y-2">
                  <h4 className="text-sm font-medium text-gray-300">Description:</h4>
                  <p className="text-sm text-gray-400">
                    {selectedEvent.data.description}
                  </p>
                </div>
              )}
            </div>

            {/* Actions */}
            <div className="flex justify-end space-x-3 p-4 border-t border-gray-700/50">
              <button
                onClick={() => setShowEventDetails(false)}
                className="px-4 py-2 text-gray-400 hover:text-white hover:bg-white/10 rounded-lg transition-colors"
              >
                Close
              </button>
              <button
                className="px-4 py-2 bg-orange-500 text-white rounded-lg hover:bg-orange-600 transition-colors"
              >
                Edit {selectedEvent.type === 'activity' ? 'Activity' : 'Task'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default CalendarIntegration;