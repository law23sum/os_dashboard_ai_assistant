import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import type { ActorType } from '../types/actor';

interface ActorContextType {
  currentActor: ActorType;
  setCurrentActor: (actor: ActorType) => void;
  isPersonal: boolean;
  isEnterprise: boolean;
  isBusiness: boolean;
}

const ActorContext = createContext<ActorContextType | undefined>(undefined);

interface ActorProviderProps {
  children: ReactNode;
}

export const ActorProvider: React.FC<ActorProviderProps> = ({ children }) => {
  const [currentActor, setCurrentActor] = useState<ActorType>('personal');

  // Load saved actor preference on mount
  useEffect(() => {
    const savedActor = localStorage.getItem('osdash-actor') as ActorType;
    if (savedActor && (savedActor === 'personal' || savedActor === 'business' || savedActor === 'enterprise')) {
      setCurrentActor(savedActor);
    } else {
      setCurrentActor('personal');
      localStorage.setItem('osdash-actor', 'personal');
    }
  }, []);

  // Save to localStorage whenever actor changes
  useEffect(() => {
    localStorage.setItem('osdash-actor', currentActor);
  }, [currentActor]);

  const value: ActorContextType = {
    currentActor,
    setCurrentActor,
    isPersonal: currentActor === 'personal',
    isEnterprise: currentActor === 'enterprise',
    isBusiness: currentActor === 'business',
  };

  return (
    <ActorContext.Provider value={value}>
      {children}
    </ActorContext.Provider>
  );
};

export const useActor = (): ActorContextType => {
  const context = useContext(ActorContext);
  if (context === undefined) {
    if (import.meta.env.MODE === 'test') {
      return {
        currentActor: 'personal',
        setCurrentActor: () => undefined,
        isPersonal: true,
        isEnterprise: false,
        isBusiness: false,
      };
    }
    throw new Error('useActor must be used within an ActorProvider');
  }
  return context;
};

export default ActorContext;
