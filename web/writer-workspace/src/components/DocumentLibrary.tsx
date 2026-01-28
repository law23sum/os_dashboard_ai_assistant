import { WriterDocument } from "../api/writer";

interface DocumentLibraryProps {
  documents: WriterDocument[];
  onOpen: (doc: WriterDocument) => void;
}

export function DocumentLibrary({ documents, onOpen }: DocumentLibraryProps) {
  if (documents.length === 0) {
    return <p className="muted">No documents yet. Create one to populate the workspace.</p>;
  }

  return (
    <div className="document-library">
      {documents.map((doc) => (
        <button key={doc.id} className={`document-card ${doc.type.toLowerCase()}`} onClick={() => onOpen(doc)}>
          <div>
            <h4>{doc.title}</h4>
            <p>{doc.summary}</p>
            <div className="document-meta">
              <span className={`status-pill status-${doc.status.toLowerCase()}`}>{doc.status}</span>
              <span>{doc.last_edited}</span>
            </div>
          </div>
          <div className="document-words">
            <div>{doc.words.toLocaleString()}</div>
            <small>words</small>
          </div>
        </button>
      ))}
    </div>
  );
}
