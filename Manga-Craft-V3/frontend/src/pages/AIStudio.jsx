import { useParams } from 'react-router-dom';
import AdaptiveLayout from '../components/aistudio/AdaptiveLayout';

function AIStudio() {
  const { projectId, conversationId } = useParams();

  return (
    <AdaptiveLayout
      projectId={projectId}
      conversationId={conversationId}
    />
  );
}

export default AIStudio;
