import React from 'react';
import BentoCard from './BentoCard';
import { HelpCircle, Music, Zap, BookOpen, Fingerprint } from 'lucide-react';

const BentoGrid = ({ onSuggestionClick }) => {
  const suggestions = [
    {
      title: "Basic Open Chords",
      description: "Learn the essential open chords to play thousands of songs.",
      prompt: "What are the basic open chords?",
      icon: BookOpen,
      className: "bento-item-large",
      style: { background: 'linear-gradient(135deg, rgba(66, 133, 244, 0.1) 0%, rgba(255, 255, 255, 0.02) 100%)', cursor: 'pointer' }
    },
    {
      title: "Chord Transitions",
      description: "Smooth out your playing from Am to G.",
      prompt: "How do I transition between Am and G?",
      icon: Zap,
      className: "",
      style: { cursor: 'pointer' }
    },
    {
      title: "Beginner Progressions",
      description: "Start strumming your first real songs.",
      prompt: "Suggest a simple chord progression for beginners.",
      icon: Music,
      className: "bento-item-tall",
      style: { cursor: 'pointer' }
    },
    {
      title: "Finger Placement",
      description: "Stop muting strings during barre chords.",
      prompt: "How do I play barre chords without muting strings?",
      icon: Fingerprint,
      className: "",
      style: { cursor: 'pointer' }
    },
    {
      title: "Music Theory",
      description: "Understand the math behind the music.",
      prompt: "Explain the Circle of Fifths in simple terms.",
      icon: HelpCircle,
      className: "bento-item-wide",
      style: { cursor: 'pointer' }
    }
  ];

  return (
    <section style={{ padding: '100px 0', position: 'relative', zIndex: 1 }}>
      <div style={{ textAlign: 'center', marginBottom: '60px' }}>
        <h2 style={{ fontSize: '3rem', fontWeight: 700, marginBottom: '16px' }}>
          <span className="text-gradient">Ask the Tutor</span>
        </h2>
        <p style={{ color: 'var(--text-secondary)', fontSize: '1.2rem', maxWidth: '500px', margin: '0 auto' }}>
          Select a topic below to start learning immediately.
        </p>
      </div>
      
      <div className="bento-grid">
        {suggestions.map((feature, index) => (
          <BentoCard 
            key={index}
            title={feature.title}
            description={feature.description}
            icon={feature.icon}
            className={feature.className}
            style={feature.style}
            delay={index * 0.1}
            onClick={() => onSuggestionClick && onSuggestionClick(feature.prompt)}
          />
        ))}
      </div>
    </section>
  );
};

export default BentoGrid;
