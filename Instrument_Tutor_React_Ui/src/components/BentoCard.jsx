import React from 'react';
import { motion } from 'framer-motion';

const BentoCard = ({ title, description, icon: Icon, className = '', delay = 0, style, onClick }) => {
  return (
    <motion.div 
      onClick={onClick}
      initial={{ opacity: 0, y: 30 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, margin: "-50px" }}
      transition={{ duration: 0.6, delay, ease: "easeOut" }}
      className={`glass-panel ${className}`}
      style={{ padding: '32px', display: 'flex', flexDirection: 'column', ...style }}
    >
      {Icon && (
        <div style={{ marginBottom: '24px', color: 'var(--neon-blue)', display: 'inline-flex', padding: '16px', borderRadius: '16px', background: 'rgba(66, 133, 244, 0.1)' }}>
          <Icon size={32} strokeWidth={1.5} />
        </div>
      )}
      <h3 style={{ fontSize: '1.5rem', fontWeight: 600, marginBottom: '12px', color: 'var(--text-primary)' }}>
        {title}
      </h3>
      <p style={{ fontSize: '1rem', color: 'var(--text-secondary)', lineHeight: 1.6, fontWeight: 300 }}>
        {description}
      </p>
    </motion.div>
  );
};

export default BentoCard;
