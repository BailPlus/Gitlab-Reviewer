const ConfirmDialog = ({ 
  isOpen, 
  onClose, 
  onConfirm, 
  title = "确认操作", 
  message,
  confirmText = "确认",
  cancelText = "取消",
  isDestructive = false 
}) => {
  if (!isOpen) return null;

  return (
    <div className="confirm-overlay" onClick={onClose}>
      <div className="confirm-dialog" onClick={(e) => e.stopPropagation()}>
        <div className="confirm-header">
          <h3>{title}</h3>
        </div>
        
        <div className="confirm-content">
          <p>{message}</p>
        </div>
        
        <div className="confirm-actions">
          <button 
            className="confirm-cancel"
            onClick={onClose}
          >
            {cancelText}
          </button>
          <button 
            className={`confirm-button ${isDestructive ? 'destructive' : ''}`}
            onClick={onConfirm}
          >
            {confirmText}
          </button>
        </div>
      </div>
      
      <style jsx>{`
        .confirm-overlay {
          position: fixed;
          top: 0;
          left: 0;
          right: 0;
          bottom: 0;
          background: rgba(0, 0, 0, 0.5);
          display: flex;
          align-items: center;
          justify-content: center;
          z-index: 1002;
        }
        
        .confirm-dialog {
          background: white;
          border-radius: 8px;
          padding: 0;
          min-width: 400px;
          max-width: 500px;
          box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
        }
        
        .confirm-header {
          padding: 20px 24px 0;
        }
        
        .confirm-header h3 {
          margin: 0;
          font-size: 18px;
          font-weight: 600;
          color: #333;
        }
        
        .confirm-content {
          padding: 16px 24px 24px;
        }
        
        .confirm-content p {
          margin: 0;
          color: #666;
          line-height: 1.5;
        }
        
        .confirm-actions {
          padding: 16px 24px 24px;
          display: flex;
          gap: 12px;
          justify-content: flex-end;
        }
        
        .confirm-cancel {
          padding: 8px 16px;
          border: 1px solid #ddd;
          background: white;
          border-radius: 6px;
          cursor: pointer;
          font-size: 14px;
        }
        
        .confirm-cancel:hover {
          background: #f5f5f5;
        }
        
        .confirm-button {
          padding: 8px 16px;
          border: none;
          background: #0070f3;
          color: white;
          border-radius: 6px;
          cursor: pointer;
          font-size: 14px;
        }
        
        .confirm-button:hover {
          background: #0051cc;
        }
        
        .confirm-button.destructive {
          background: #dc3545;
        }
        
        .confirm-button.destructive:hover {
          background: #c82333;
        }
      `}</style>
    </div>
  );
};

export default ConfirmDialog;
