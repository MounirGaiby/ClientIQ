import React, { useState, useEffect } from 'react';
import {
  DndContext,
  closestCenter,
  KeyboardSensor,
  PointerSensor,
  useSensor,
  useSensors,
  DragEndEvent,
  DragOverEvent,
} from '@dnd-kit/core';
import {
  arrayMove,
  SortableContext,
  sortableKeyboardCoordinates,
  verticalListSortingStrategy,
} from '@dnd-kit/sortable';
import {
  useSortable,
} from '@dnd-kit/sortable';
import { CSS } from '@dnd-kit/utilities';
import {
  Plus,
  DollarSign,
  Calendar,
  User,
  Building,
  Edit,
  Trash2,
  Eye,
  Phone,
  Mail,
  MoreHorizontal
} from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import OpportunityModal from './OpportunityModal';
import { pipelineApi } from '../api/pipeline';

interface SalesStage {
  id: number;
  name: string;
  description: string;
  order: number;
  probability: number;
  is_closed_won: boolean;
  is_closed_lost: boolean;
  is_active: boolean;
  color: string;
  opportunities_count?: number;
  total_value?: number;
}

interface Opportunity {
  id: number;
  name: string;
  description: string;
  value: number;
  probability: number;
  stage: SalesStage;
  contact: {
    id: number;
    first_name: string;
    last_name: string;
    email: string;
    phone: string;
  };
  company: {
    id: number;
    name: string;
  } | null;
  owner: {
    id: number;
    first_name: string;
    last_name: string;
  };
  expected_close_date: string;
  priority: 'low' | 'medium' | 'high';
  created_at: string;
  updated_at: string;
}

interface PipelineData {
  stage: SalesStage;
  opportunities: Opportunity[];
  summary: {
    count: number;
    total_value: number;
    weighted_value: number;
  };
}

// Sortable Opportunity Card Component
function SortableOpportunity({ opportunity, onEdit }: { opportunity: Opportunity; onEdit: (opp: Opportunity) => void }) {
  const {
    attributes,
    listeners,
    setNodeRef,
    transform,
    transition,
    isDragging,
  } = useSortable({ id: opportunity.id });

  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
    opacity: isDragging ? 0.5 : 1,
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(amount);
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high': return 'bg-red-500';
      case 'medium': return 'bg-yellow-500';
      case 'low': return 'bg-green-500';
      default: return 'bg-gray-500';
    }
  };

  return (
    <div
      ref={setNodeRef}
      style={style}
      {...attributes}
      {...listeners}
      className="bg-white/5 rounded-lg p-3 border border-gray-600 hover:border-orange-500/50 transition-all cursor-pointer"
      onClick={() => onEdit(opportunity)}
    >
      <div className="space-y-2">
        <div className="flex items-start justify-between">
          <h4 className="font-medium text-white text-sm line-clamp-2">
            {opportunity.name}
          </h4>
          <div className="flex items-center space-x-1">
            <div
              className={`w-2 h-2 rounded-full ${getPriorityColor(opportunity.priority)}`}
            ></div>
            <button className="text-gray-400 hover:text-white p-1">
              <MoreHorizontal className="h-3 w-3" />
            </button>
          </div>
        </div>

        <div className="flex items-center text-green-400 font-medium">
          <DollarSign className="h-3 w-3 mr-1" />
          <span className="text-sm">{formatCurrency(opportunity.value)}</span>
        </div>

        <div className="space-y-1 text-xs text-gray-300">
          <div className="flex items-center">
            <User className="h-3 w-3 mr-1" />
            <span className="truncate">
              {opportunity.contact.first_name} {opportunity.contact.last_name}
            </span>
          </div>
          {opportunity.company && (
            <div className="flex items-center">
              <Building className="h-3 w-3 mr-1" />
              <span className="truncate">{opportunity.company.name}</span>
            </div>
          )}
          <div className="flex items-center">
            <Calendar className="h-3 w-3 mr-1" />
            <span>
              {new Date(opportunity.expected_close_date).toLocaleDateString()}
            </span>
          </div>
        </div>

        <div className="flex items-center justify-between pt-2">
          <span className="text-xs text-gray-400">
            {opportunity.probability}% probability
          </span>
          <div className="flex items-center space-x-1">
            <button
              onClick={(e) => {
                e.stopPropagation();
                window.location.href = `mailto:${opportunity.contact.email}`;
              }}
              className="text-gray-400 hover:text-orange-400 p-1"
            >
              <Mail className="h-3 w-3" />
            </button>
            <button
              onClick={(e) => {
                e.stopPropagation();
                window.location.href = `tel:${opportunity.contact.phone}`;
              }}
              className="text-gray-400 hover:text-orange-400 p-1"
            >
              <Phone className="h-3 w-3" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

// Droppable Stage Column Component
function DroppableStage({ 
  stageData, 
  onEdit 
}: { 
  stageData: PipelineData; 
  onEdit: (opp: Opportunity) => void;
}) {
  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(amount);
  };

  return (
    <div className="min-w-80 bg-gradient-to-b from-slate-800/50 to-slate-900/50 backdrop-blur-xl border border-orange-500/20 rounded-xl shadow-2xl">
      {/* Stage Header */}
      <div className="p-4 border-b border-gray-700">
        <div className="flex items-center justify-between mb-2">
          <h3 className="font-semibold text-white flex items-center">
            <div
              className="w-3 h-3 rounded-full mr-2"
              style={{ backgroundColor: stageData.stage.color }}
            ></div>
            {stageData.stage.name}
          </h3>
          <span className="text-xs bg-gray-700 text-gray-300 px-2 py-1 rounded">
            {stageData.summary.count}
          </span>
        </div>
        <div className="text-sm text-gray-300">
          <div>Value: {formatCurrency(stageData.summary.total_value)}</div>
          <div>Weighted: {formatCurrency(stageData.summary.weighted_value)}</div>
          <div>Probability: {stageData.stage.probability}%</div>
        </div>
      </div>

      {/* Opportunities List */}
      <div className="p-4 space-y-3 min-h-96">
        <SortableContext 
          items={stageData.opportunities.map(opp => opp.id)} 
          strategy={verticalListSortingStrategy}
        >
          {stageData.opportunities.map((opportunity) => (
            <SortableOpportunity
              key={opportunity.id}
              opportunity={opportunity}
              onEdit={onEdit}
            />
          ))}
        </SortableContext>

        {/* Empty State */}
        {stageData.opportunities.length === 0 && (
          <div className="text-center py-8 text-gray-400">
            <div className="text-4xl mb-2">📋</div>
            <p className="text-sm">No opportunities in this stage</p>
          </div>
        )}
      </div>
    </div>
  );
}

const PipelineManagement: React.FC = () => {
  const [pipelineData, setPipelineData] = useState<PipelineData[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedOpportunity, setSelectedOpportunity] = useState<Opportunity | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isCreating, setIsCreating] = useState(false);
  const { user } = useAuth();

  const sensors = useSensors(
    useSensor(PointerSensor),
    useSensor(KeyboardSensor, {
      coordinateGetter: sortableKeyboardCoordinates,
    })
  );

  useEffect(() => {
    fetchPipelineData();
  }, []);

  const fetchPipelineData = async () => {
    try {
      setLoading(true);
      const data = await pipelineApi.getPipeline();
      setPipelineData(data.pipeline);
    } catch (error) {
      console.error('Error fetching pipeline data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleDragEnd = async (event: DragEndEvent) => {
    const { active, over } = event;

    if (!over) return;

    const opportunityId = Number(active.id);
    const newStageId = Number(over.id);

    // Find the opportunity and its current stage
    let sourceStage: PipelineData | undefined;
    let opportunity: Opportunity | undefined;

    for (const stage of pipelineData) {
      const opp = stage.opportunities.find(o => o.id === opportunityId);
      if (opp) {
        sourceStage = stage;
        opportunity = opp;
        break;
      }
    }

    if (!opportunity || !sourceStage) return;
    if (opportunity.stage.id === newStageId) return;

    const targetStage = pipelineData.find(stage => stage.stage.id === newStageId);
    if (!targetStage) return;

    try {
      // Optimistic update
      const newPipelineData = [...pipelineData];
      const sourceIndex = newPipelineData.findIndex(s => s.stage.id === sourceStage.stage.id);
      const targetIndex = newPipelineData.findIndex(s => s.stage.id === newStageId);

      // Remove from source
      newPipelineData[sourceIndex].opportunities = sourceStage.opportunities.filter(
        opp => opp.id !== opportunityId
      );

      // Add to target
      const updatedOpportunity = { ...opportunity, stage: targetStage.stage };
      newPipelineData[targetIndex].opportunities.push(updatedOpportunity);

      setPipelineData(newPipelineData);

      // API call to update stage
      await pipelineApi.changeOpportunityStage(opportunityId, newStageId);

      // Refresh data to get accurate totals
      await fetchPipelineData();
    } catch (error) {
      console.error('Error moving opportunity:', error);
      // Revert optimistic update
      fetchPipelineData();
    }
  };

  const handleCreateOpportunity = () => {
    setSelectedOpportunity(null);
    setIsCreating(true);
    setIsModalOpen(true);
  };

  const handleEditOpportunity = (opportunity: Opportunity) => {
    setSelectedOpportunity(opportunity);
    setIsCreating(false);
    setIsModalOpen(true);
  };

  const handleOpportunitySaved = () => {
    setIsModalOpen(false);
    fetchPipelineData();
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(amount);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-96">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-orange-500"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-white">Sales Pipeline</h2>
          <p className="text-gray-300">
            Manage your opportunities and track progress through sales stages
          </p>
        </div>
        <button
          onClick={handleCreateOpportunity}
          className="bg-gradient-to-r from-orange-500 to-pink-500 text-white px-4 py-2 rounded-lg font-semibold shadow-lg hover:shadow-xl transition-all duration-200 flex items-center space-x-2"
        >
          <Plus className="h-4 w-4" />
          <span>New Opportunity</span>
        </button>
      </div>

      {/* Pipeline Summary */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        <div className="bg-gradient-to-r from-slate-800/50 to-slate-700/50 backdrop-blur-xl border border-orange-500/20 rounded-lg p-4">
          <h3 className="text-sm font-medium text-gray-300">Total Pipeline Value</h3>
          <p className="text-2xl font-bold text-white mt-1">
            {formatCurrency(
              pipelineData.reduce((sum, stage) => sum + stage.summary.total_value, 0)
            )}
          </p>
        </div>
        <div className="bg-gradient-to-r from-slate-800/50 to-slate-700/50 backdrop-blur-xl border border-orange-500/20 rounded-lg p-4">
          <h3 className="text-sm font-medium text-gray-300">Weighted Value</h3>
          <p className="text-2xl font-bold text-white mt-1">
            {formatCurrency(
              pipelineData.reduce((sum, stage) => sum + stage.summary.weighted_value, 0)
            )}
          </p>
        </div>
        <div className="bg-gradient-to-r from-slate-800/50 to-slate-700/50 backdrop-blur-xl border border-orange-500/20 rounded-lg p-4">
          <h3 className="text-sm font-medium text-gray-300">Total Opportunities</h3>
          <p className="text-2xl font-bold text-white mt-1">
            {pipelineData.reduce((sum, stage) => sum + stage.summary.count, 0)}
          </p>
        </div>
      </div>

      {/* Pipeline Board */}
      <DndContext
        sensors={sensors}
        collisionDetection={closestCenter}
        onDragEnd={handleDragEnd}
      >
        <div className="flex space-x-4 overflow-x-auto pb-4">
          {pipelineData.map((stageData) => (
            <SortableContext
              key={stageData.stage.id}
              items={[stageData.stage.id]}
              strategy={verticalListSortingStrategy}
            >
              <DroppableStage 
                stageData={stageData} 
                onEdit={handleEditOpportunity}
              />
            </SortableContext>
          ))}
        </div>
      </DndContext>

      {/* Opportunity Modal */}
      {isModalOpen && (
        <OpportunityModal
          opportunity={selectedOpportunity}
          isOpen={isModalOpen}
          isCreating={isCreating}
          onClose={() => setIsModalOpen(false)}
          onSave={handleOpportunitySaved}
        />
      )}
    </div>
  );
};

export default PipelineManagement;