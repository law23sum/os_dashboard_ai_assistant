import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { ActorType } from '../components/ActorSwitch';

interface ActorContextType {
  currentActor: ActorType;
  setCurrentActor: (actor: ActorType) => void;
  isPersonal: boolean;
  isEnterprise: boolean;
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
    if (savedActor && (savedActor === 'personal' || savedActor === 'enterprise')) {
      setCurrentActor(savedActor);
    } else {
      // Default to personal for new users
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
    throw new Error('useActor must be used within an ActorProvider');
  }
  return context;
};

export default ActorContext;



