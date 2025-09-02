/**
 * 通用UI相关的自定义Hook
 */
import { useState, useEffect } from 'react';

// 打字机效果Hook
export const useTypewriter = (text, delay = 100, trigger = true) => {
  const [displayText, setDisplayText] = useState('');

  useEffect(() => {
    if (!trigger) {
      setDisplayText('');
      return;
    }

    let i = 0;
    setDisplayText('');
    
    const interval = setInterval(() => {
      setDisplayText(text.substring(0, i + 1));
      i++;
      
      if (i >= text.length) {
        clearInterval(interval);
      }
    }, delay);

    return () => clearInterval(interval);
  }, [text, delay, trigger]);

  return displayText;
};

// 模态框Hook
export const useModal = (initialState = false) => {
  const [isOpen, setIsOpen] = useState(initialState);

  const open = () => setIsOpen(true);
  const close = () => setIsOpen(false);
  const toggle = () => setIsOpen(!isOpen);

  return {
    isOpen,
    open,
    close,
    toggle,
  };
};
