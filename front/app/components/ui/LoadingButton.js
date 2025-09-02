const LoadingButton = ({ 
  children, 
  isLoading = false, 
  disabled = false, 
  className = '', 
  onClick,
  ...props 
}) => {
  return (
    <button
      className={className}
      onClick={onClick}
      disabled={disabled || isLoading}
      {...props}
    >
      {isLoading && (
        <svg
          className="loading-spinner"
          width="16"
          height="16"
          viewBox="0 0 24 24"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
          style={{ 
            marginRight: '8px',
            animation: 'spin 1s linear infinite'
          }}
        >
          <circle
            cx="12"
            cy="12"
            r="10"
            stroke="currentColor"
            strokeWidth="2"
            strokeDasharray="31.416"
            strokeDashoffset="31.416"
            style={{
              animation: 'dash 2s ease-in-out infinite'
            }}
          />
        </svg>
      )}
      {children}
      
      <style jsx>{`
        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }
        
        @keyframes dash {
          0% {
            stroke-dasharray: 1, 200;
            stroke-dashoffset: 0;
          }
          50% {
            stroke-dasharray: 100, 200;
            stroke-dashoffset: -15;
          }
          100% {
            stroke-dasharray: 100, 200;
            stroke-dashoffset: -125;
          }
        }
      `}</style>
    </button>
  );
};

export default LoadingButton;
