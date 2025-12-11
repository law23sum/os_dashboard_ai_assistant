import { WriterDocument } from "../api/writer";

interface DocumentLibraryProps {
  documents: WriterDocument[];
  onOpen: (doc: WriterDocument) => void;
}

export function DocumentLibrary({ documents, onOpen }: DocumentLibraryProps) {
  return (
    <div className="document-library">
      {documents.map((doc) => (
        <button
          key={doc.id}
          className={`document-card ${doc.type.toLowerCase()}`}
          onClick={() => onOpen(doc)}
        >
          <div>
            <h4>{doc.title}</h4>
            <p>{doc.summary}</p>
            <div className="document-meta">
              <span className={`status-pill status-${doc.status.toLowerCase()}`}>
                {doc.status}
              </span>
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
