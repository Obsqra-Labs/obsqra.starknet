'use client';

interface DataPathStep {
  id: string;
  label: string;
  description: string;
  status: 'pending' | 'active' | 'complete' | 'error';
  data?: any;
}

interface DataPathVisualizationProps {
  steps: DataPathStep[];
  currentStep?: string;
  className?: string;
}

export function DataPathVisualization({ 
  steps, 
  currentStep,
  className = '' 
}: DataPathVisualizationProps) {
  const getStepIcon = (step: DataPathStep) => {
    if (step.status === 'complete') {
      return (
        <svg className="w-5 h-5 text-emerald-400" fill="currentColor" viewBox="0 0 20 20">
          <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
        </svg>
      );
    }
    if (step.status === 'active') {
      return (
        <svg className="w-5 h-5 text-blue-400 animate-spin" fill="none" viewBox="0 0 24 24">
          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
      );
    }
    if (step.status === 'error') {
      return (
        <svg className="w-5 h-5 text-red-400" fill="currentColor" viewBox="0 0 20 20">
          <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
        </svg>
      );
    }
    return (
      <svg className="w-5 h-5 text-white/30" fill="currentColor" viewBox="0 0 20 20">
        <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm0-2a6 6 0 100-12 6 6 0 000 12z" clipRule="evenodd" />
      </svg>
    );
  };

  const getStepColor = (step: DataPathStep) => {
    if (step.status === 'complete') return 'text-emerald-400 border-emerald-400/40';
    if (step.status === 'active') return 'text-blue-400 border-blue-400/40';
    if (step.status === 'error') return 'text-red-400 border-red-400/40';
    return 'text-white/40 border-white/10';
  };

  return (
    <div className={`bg-[#111113] border border-white/10 rounded-xl p-6 ${className}`}>
      <div className="mb-4">
        <p className="text-xs uppercase tracking-[0.3em] text-white/40">Data Path</p>
        <h3 className="text-lg font-semibold">zkML Proof Pipeline</h3>
      </div>

      <div className="space-y-4">
        {steps.map((step, index) => (
          <div key={step.id} className="relative">
            {/* Connection Line */}
            {index > 0 && (
              <div className={`absolute left-[10px] top-0 w-0.5 h-4 ${
                steps[index - 1].status === 'complete' 
                  ? 'bg-emerald-400/40' 
                  : 'bg-white/10'
              }`} style={{ transform: 'translateY(-100%)' }} />
            )}

            {/* Step */}
            <div className={`flex items-start gap-4 p-4 rounded-lg border transition-colors ${
              step.status === 'active' 
                ? 'bg-blue-500/10 border-blue-400/40' 
                : step.status === 'complete'
                ? 'bg-emerald-500/5 border-emerald-400/20'
                : 'bg-white/5 border-white/10'
            }`}>
              <div className={`flex-shrink-0 mt-0.5 ${getStepColor(step)}`}>
                {getStepIcon(step)}
              </div>
              <div className="flex-1 min-w-0">
                <div className="flex items-center justify-between mb-1">
                  <h4 className={`font-semibold ${getStepColor(step)}`}>
                    {step.label}
                  </h4>
                  {step.status === 'active' && (
                    <span className="text-xs text-blue-400 animate-pulse">Processing...</span>
                  )}
                </div>
                <p className="text-sm text-white/60">{step.description}</p>
                {step.data && step.status === 'complete' && (
                  <div className="mt-2 text-xs text-white/50 font-mono">
                    {typeof step.data === 'string' ? step.data : JSON.stringify(step.data, null, 2)}
                  </div>
                )}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
