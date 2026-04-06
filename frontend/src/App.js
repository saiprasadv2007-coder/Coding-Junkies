import { useState, useEffect, useRef } from "react";
import "@/App.css";
import axios from "axios";
import { Button } from "./components/ui/button";
import { ScrollArea } from "./components/ui/scroll-area";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "./components/ui/tabs";
import { 
  Play, 
  Pause, 
  Volume2, 
  VolumeX,
  Loader2,
  Sparkles,
  Waves,
  Eye,
  Brain,
  History,
  ChevronRight
} from "lucide-react";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Waveform Visualizer Component
const WaveformVisualizer = ({ isPlaying }) => {
  return (
    <div className="flex items-center justify-center gap-1 h-8">
      {[...Array(8)].map((_, i) => (
        <div
          key={i}
          className={`w-1 bg-[#D9F268] rounded-full transition-all ${
            isPlaying ? 'waveform-bar' : 'h-1'
          }`}
          style={{ 
            height: isPlaying ? undefined : '4px',
            animationDelay: `${i * 0.1}s` 
          }}
        />
      ))}
    </div>
  );
};

// Audio Player Component
const AudioPlayer = ({ vocalization, onAnalyze, isAnalyzing }) => {
  const audioRef = useRef(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [isMuted, setIsMuted] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);

  useEffect(() => {
    if (audioRef.current) {
      audioRef.current.pause();
      setIsPlaying(false);
      setCurrentTime(0);
    }
  }, [vocalization]);

  const togglePlay = () => {
    if (audioRef.current) {
      if (isPlaying) {
        audioRef.current.pause();
      } else {
        audioRef.current.play().catch(() => {
          // Audio play failed - likely no audio file
        });
      }
      setIsPlaying(!isPlaying);
    }
  };

  const toggleMute = () => {
    if (audioRef.current) {
      audioRef.current.muted = !isMuted;
      setIsMuted(!isMuted);
    }
  };

  const formatTime = (time) => {
    const mins = Math.floor(time / 60);
    const secs = Math.floor(time % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  if (!vocalization) {
    return (
      <div className="widget" data-testid="audio-player-empty">
        <div className="widget-header">Audio Player</div>
        <div className="flex items-center justify-center h-32 text-[#828C85]">
          Select a vocalization to play
        </div>
      </div>
    );
  }

  return (
    <div className="widget" data-testid="audio-player">
      <div className="widget-header flex items-center gap-2">
        <Waves className="w-4 h-4" />
        Vocalization: {vocalization.name}
      </div>
      
      <audio
        ref={audioRef}
        src={vocalization.audio_url}
        onTimeUpdate={() => setCurrentTime(audioRef.current?.currentTime || 0)}
        onLoadedMetadata={() => setDuration(audioRef.current?.duration || 0)}
        onEnded={() => setIsPlaying(false)}
      />
      
      <div className="space-y-4">
        <WaveformVisualizer isPlaying={isPlaying} />
        
        <div className="flex items-center gap-4">
          <Button
            variant="ghost"
            size="icon"
            onClick={togglePlay}
            className="audio-control-btn h-10 w-10 rounded-full border border-[#232724]"
            data-testid="audio-play-btn"
          >
            {isPlaying ? (
              <Pause className="h-5 w-5 text-[#D9F268]" />
            ) : (
              <Play className="h-5 w-5 text-[#D9F268]" />
            )}
          </Button>
          
          <div className="flex-1">
            <div className="h-1 bg-[#232724] rounded-full overflow-hidden">
              <div 
                className="h-full bg-[#D9F268] transition-all"
                style={{ width: `${duration ? (currentTime / duration) * 100 : 0}%` }}
              />
            </div>
            <div className="flex justify-between mt-1 text-xs font-mono text-[#828C85]">
              <span>{formatTime(currentTime)}</span>
              <span>{formatTime(duration)}</span>
            </div>
          </div>
          
          <Button
            variant="ghost"
            size="icon"
            onClick={toggleMute}
            className="audio-control-btn h-8 w-8"
            data-testid="audio-mute-btn"
          >
            {isMuted ? (
              <VolumeX className="h-4 w-4 text-[#828C85]" />
            ) : (
              <Volume2 className="h-4 w-4 text-[#828C85]" />
            )}
          </Button>
        </div>
        
        <div className="p-3 bg-[#0A0B0A] rounded border border-[#232724]">
          <div className="text-xs font-mono text-[#828C85] uppercase tracking-wider mb-1">Context</div>
          <div className="text-sm text-[#E8F0E5]">{vocalization.context}</div>
          <div className="text-xs text-[#828C85] mt-2">{vocalization.description}</div>
        </div>
        
        <Button
          onClick={() => onAnalyze('vocalization', vocalization.id)}
          disabled={isAnalyzing}
          className="w-full bg-[#D9F268] text-black hover:bg-[#c9e258] font-semibold"
          data-testid="analyze-vocalization-btn"
        >
          {isAnalyzing ? (
            <>
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              Analyzing...
            </>
          ) : (
            <>
              <Brain className="mr-2 h-4 w-4" />
              Translate to Human Language
            </>
          )}
        </Button>
      </div>
    </div>
  );
};

// Expression Card Component
const ExpressionCard = ({ expression, isSelected, onClick }) => {
  return (
    <button
      onClick={onClick}
      className={`expression-card w-full p-3 rounded text-left ${isSelected ? 'selected' : ''}`}
      data-testid={`expression-card-${expression.id}`}
    >
      <div className="flex items-start justify-between">
        <div>
          <div className="font-semibold text-[#E8F0E5] text-sm">{expression.name}</div>
          <div className="text-xs text-[#FF6B4A] mt-1">{expression.emotion}</div>
        </div>
        {isSelected && <Eye className="w-4 h-4 text-[#FF6B4A]" />}
      </div>
      <div className="text-xs text-[#828C85] mt-2 italic">"{expression.meaning}"</div>
    </button>
  );
};

// Analysis Result Component
const AnalysisResult = ({ result, isLoading }) => {
  if (isLoading) {
    return (
      <div className="widget h-full" data-testid="analysis-loading">
        <div className="widget-header flex items-center gap-2">
          <Sparkles className="w-4 h-4 text-[#D9F268]" />
          AI Analysis
        </div>
        <div className="flex flex-col items-center justify-center h-48 space-y-4">
          <div className="relative">
            <Loader2 className="w-8 h-8 text-[#D9F268] animate-spin" />
          </div>
          <div className="text-[#828C85] font-mono text-sm">
            Processing communication signal<span className="loading-dots"></span>
          </div>
        </div>
      </div>
    );
  }

  if (!result) {
    return (
      <div className="widget h-full" data-testid="analysis-empty">
        <div className="widget-header flex items-center gap-2">
          <Sparkles className="w-4 h-4" />
          AI Interpretation
        </div>
        <div className="flex flex-col items-center justify-center h-48 text-[#828C85] space-y-2">
          <Brain className="w-12 h-12 opacity-30" />
          <p className="text-center text-sm">
            Select a vocalization or expression and click analyze<br />
            to translate to human language
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="widget h-full" data-testid="analysis-result">
      <div className="widget-header flex items-center gap-2">
        <Sparkles className="w-4 h-4 text-[#D9F268]" />
        AI Interpretation - {result.animal} {result.input_type}
      </div>
      
      <div className="space-y-4">
        <div className="p-4 bg-[#0A0B0A] rounded border border-[#D9F268]/30">
          <div className="text-xs font-mono text-[#D9F268] uppercase tracking-wider mb-2">
            Human Translation
          </div>
          <div className="translation-text">
            "{result.human_translation}"
          </div>
        </div>
        
        <div className="p-3 bg-[#0A0B0A] rounded border border-[#232724]">
          <div className="text-xs font-mono text-[#FF6B4A] uppercase tracking-wider mb-2">
            Context
          </div>
          <div className="text-sm text-[#E8F0E5]">
            {result.context_meaning}
          </div>
        </div>
        
        <div className="p-3 bg-[#0A0B0A] rounded border border-[#232724]">
          <div className="text-xs font-mono text-[#4ADE80] uppercase tracking-wider mb-2">
            Behavioral Insight
          </div>
          <div className="text-sm text-[#E8F0E5]">
            {result.behavioral_insight}
          </div>
        </div>
        
        <div className="text-xs font-mono text-[#828C85] text-right">
          Analyzed: {new Date(result.timestamp).toLocaleString()}
        </div>
      </div>
    </div>
  );
};

// Animal Selection Card
const AnimalCard = ({ animal, isSelected, onClick }) => {
  return (
    <button
      onClick={onClick}
      className={`animal-card p-3 rounded text-left w-full ${isSelected ? 'selected' : ''}`}
      data-testid={`animal-card-${animal.id}`}
    >
      <div className="flex items-center gap-3">
        <img 
          src={animal.image} 
          alt={animal.name}
          className="w-12 h-12 rounded object-cover"
        />
        <div className="flex-1 min-w-0">
          <div className="font-semibold text-[#E8F0E5] truncate">{animal.name}</div>
          <div className="text-xs text-[#828C85] truncate">{animal.scientific_name}</div>
        </div>
        {isSelected && <ChevronRight className="w-4 h-4 text-[#D9F268]" />}
      </div>
    </button>
  );
};

// Main App Component
function App() {
  const [animals, setAnimals] = useState([]);
  const [selectedAnimal, setSelectedAnimal] = useState(null);
  const [animalData, setAnimalData] = useState(null);
  const [selectedVocalization, setSelectedVocalization] = useState(null);
  const [selectedExpression, setSelectedExpression] = useState(null);
  const [analysisResult, setAnalysisResult] = useState(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisHistory, setAnalysisHistory] = useState([]);
  const [activeTab, setActiveTab] = useState("vocalizations");
  const [isLoading, setIsLoading] = useState(true);

  // Fetch animals on mount
  useEffect(() => {
    fetchAnimals();
    fetchHistory();
  }, []);

  // Fetch animal details when selected
  useEffect(() => {
    if (selectedAnimal) {
      fetchAnimalData(selectedAnimal.id);
    }
  }, [selectedAnimal]);

  const fetchAnimals = async () => {
    try {
      const response = await axios.get(`${API}/animals`);
      setAnimals(response.data.animals);
      if (response.data.animals.length > 0) {
        setSelectedAnimal(response.data.animals[0]);
      }
      setIsLoading(false);
    } catch (error) {
      console.error("Failed to fetch animals:", error);
      setIsLoading(false);
    }
  };

  const fetchAnimalData = async (animalId) => {
    try {
      const response = await axios.get(`${API}/animals/${animalId}`);
      setAnimalData(response.data);
      setSelectedVocalization(null);
      setSelectedExpression(null);
      setAnalysisResult(null);
    } catch (error) {
      console.error("Failed to fetch animal data:", error);
    }
  };

  const fetchHistory = async () => {
    try {
      const response = await axios.get(`${API}/analysis/history?limit=10`);
      setAnalysisHistory(response.data.history);
    } catch (error) {
      console.error("Failed to fetch history:", error);
    }
  };

  const handleAnalyze = async (type, id) => {
    if (!selectedAnimal) return;
    
    setIsAnalyzing(true);
    setAnalysisResult(null);
    
    try {
      const payload = {
        animal_id: selectedAnimal.id,
        ...(type === 'vocalization' ? { vocalization_id: id } : { expression_id: id })
      };
      
      const response = await axios.post(`${API}/analyze`, payload);
      setAnalysisResult(response.data);
      fetchHistory();
    } catch (error) {
      console.error("Analysis failed:", error);
    } finally {
      setIsAnalyzing(false);
    }
  };

  if (isLoading) {
    return (
      <div className="app-container flex items-center justify-center min-h-screen">
        <Loader2 className="w-8 h-8 text-[#D9F268] animate-spin" />
      </div>
    );
  }

  return (
    <div className="app-container" data-testid="app-container">
      {/* Scanline effect */}
      <div className="scanline" />
      
      {/* Header */}
      <header className="border-b border-[#232724] bg-[#121413]">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="font-heading text-2xl sm:text-3xl font-black tracking-tight text-[#E8F0E5] uppercase">
                Animal <span className="text-[#D9F268]">Voice</span> Lab
              </h1>
              <p className="text-xs font-mono text-[#828C85] tracking-wider mt-1">
                COMMUNICATION PATTERN ANALYSIS SYSTEM
              </p>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-2 h-2 rounded-full bg-[#4ADE80] animate-pulse" />
              <span className="text-xs font-mono text-[#828C85]">SYSTEM ONLINE</span>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-6">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-4">
          
          {/* Left Panel - Animal Selection */}
          <div className="lg:col-span-3 space-y-4">
            <div className="widget">
              <div className="widget-header">Select Subject</div>
              <ScrollArea className="h-[400px] lg:h-[calc(100vh-280px)]">
                <div className="space-y-2 pr-2">
                  {animals.map((animal) => (
                    <AnimalCard
                      key={animal.id}
                      animal={animal}
                      isSelected={selectedAnimal?.id === animal.id}
                      onClick={() => setSelectedAnimal(animal)}
                    />
                  ))}
                </div>
              </ScrollArea>
            </div>
          </div>

          {/* Center Panel - Animal Details & Analysis */}
          <div className="lg:col-span-5 space-y-4">
            {animalData && (
              <>
                {/* Animal Hero */}
                <div className="widget p-0 overflow-hidden" data-testid="animal-hero">
                  <div className="relative h-48">
                    <img 
                      src={animalData.image} 
                      alt={animalData.name}
                      className="w-full h-full object-cover"
                    />
                    <div className="absolute inset-0 bg-gradient-to-t from-[#0A0B0A] via-transparent to-transparent" />
                    <div className="absolute bottom-0 left-0 p-4">
                      <h2 className="font-heading text-3xl font-bold text-[#E8F0E5]">
                        {animalData.name}
                      </h2>
                      <p className="text-sm font-mono text-[#828C85] italic">
                        {animalData.scientific_name}
                      </p>
                    </div>
                  </div>
                </div>

                {/* Tabs for Vocalizations/Expressions */}
                <Tabs value={activeTab} onValueChange={setActiveTab} className="widget p-0">
                  <TabsList className="w-full bg-[#0A0B0A] border-b border-[#232724] rounded-none p-0">
                    <TabsTrigger 
                      value="vocalizations"
                      className="flex-1 rounded-none py-3 data-[state=active]:bg-transparent data-[state=active]:text-[#D9F268] data-[state=active]:border-b-2 data-[state=active]:border-[#D9F268] font-mono text-xs uppercase tracking-wider"
                      data-testid="tab-vocalizations"
                    >
                      <Waves className="w-4 h-4 mr-2" />
                      Vocalizations
                    </TabsTrigger>
                    <TabsTrigger 
                      value="expressions"
                      className="flex-1 rounded-none py-3 data-[state=active]:bg-transparent data-[state=active]:text-[#FF6B4A] data-[state=active]:border-b-2 data-[state=active]:border-[#FF6B4A] font-mono text-xs uppercase tracking-wider"
                      data-testid="tab-expressions"
                    >
                      <Eye className="w-4 h-4 mr-2" />
                      Expressions
                    </TabsTrigger>
                  </TabsList>
                  
                  <TabsContent value="vocalizations" className="p-4 mt-0">
                    <div className="grid grid-cols-2 gap-2 mb-4">
                      {animalData.vocalizations?.map((v) => (
                        <button
                          key={v.id}
                          onClick={() => setSelectedVocalization(v)}
                          className={`p-3 rounded text-left border transition-all ${
                            selectedVocalization?.id === v.id
                              ? 'border-[#D9F268] bg-[#D9F268]/10'
                              : 'border-[#232724] hover:border-[#D9F268]/50'
                          }`}
                          data-testid={`vocalization-btn-${v.id}`}
                        >
                          <div className="font-semibold text-sm text-[#E8F0E5]">{v.name}</div>
                          <div className="text-xs text-[#828C85] mt-1">{v.context}</div>
                        </button>
                      ))}
                    </div>
                    <AudioPlayer 
                      vocalization={selectedVocalization} 
                      onAnalyze={handleAnalyze}
                      isAnalyzing={isAnalyzing}
                    />
                  </TabsContent>
                  
                  <TabsContent value="expressions" className="p-4 mt-0">
                    <div className="space-y-2 mb-4">
                      {animalData.expressions?.map((e) => (
                        <ExpressionCard
                          key={e.id}
                          expression={e}
                          isSelected={selectedExpression?.id === e.id}
                          onClick={() => setSelectedExpression(e)}
                        />
                      ))}
                    </div>
                    {selectedExpression && (
                      <Button
                        onClick={() => handleAnalyze('expression', selectedExpression.id)}
                        disabled={isAnalyzing}
                        className="w-full bg-[#FF6B4A] text-white hover:bg-[#e85a3a] font-semibold"
                        data-testid="analyze-expression-btn"
                      >
                        {isAnalyzing ? (
                          <>
                            <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                            Analyzing...
                          </>
                        ) : (
                          <>
                            <Brain className="mr-2 h-4 w-4" />
                            Translate Expression
                          </>
                        )}
                      </Button>
                    )}
                  </TabsContent>
                </Tabs>
              </>
            )}
          </div>

          {/* Right Panel - Analysis Results */}
          <div className="lg:col-span-4 space-y-4">
            <AnalysisResult result={analysisResult} isLoading={isAnalyzing} />
            
            {/* History */}
            <div className="widget">
              <div className="widget-header flex items-center gap-2">
                <History className="w-4 h-4" />
                Recent Analyses
              </div>
              <ScrollArea className="h-48">
                {analysisHistory.length > 0 ? (
                  <div className="space-y-2 pr-2">
                    {analysisHistory.map((record) => (
                      <div 
                        key={record.id}
                        className="p-2 bg-[#0A0B0A] rounded border border-[#232724] text-xs"
                        data-testid={`history-item-${record.id}`}
                      >
                        <div className="flex items-center justify-between">
                          <span className="font-semibold text-[#E8F0E5]">
                            {record.animal_name}
                          </span>
                          <span className="text-[#828C85] font-mono">
                            {record.input_type}
                          </span>
                        </div>
                        <div className="text-[#D9F268] mt-1 truncate">
                          "{record.human_translation}"
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-center text-[#828C85] py-8 text-sm">
                    No analysis history yet
                  </div>
                )}
              </ScrollArea>
            </div>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="border-t border-[#232724] bg-[#121413] mt-8">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between text-xs font-mono text-[#828C85]">
            <span>ANIMAL VOICE LAB v1.0</span>
            <span>POWERED BY GEMINI AI</span>
          </div>
        </div>
      </footer>
    </div>
  );
}

export default App;
