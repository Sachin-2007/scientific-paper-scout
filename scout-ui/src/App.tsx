import { MantineProvider } from '@mantine/core';
import { PaperScout } from './components/PaperScout';

function App() {
  return (
    <MantineProvider>
      <PaperScout />
    </MantineProvider>
  );
}

export default App;
