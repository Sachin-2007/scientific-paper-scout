import { useState, useEffect } from 'react';
import { TextInput, NumberInput, Button, Paper, Text, Group, Stack, Loader, Card, Image, Badge, Container, Title, Box, Mark, Alert } from '@mantine/core';
import axios from 'axios';
import ReactMarkdown from 'react-markdown';

interface Title {
  type: 'title';
  title: string;
  url: string;
  latency: number;
}

interface Summary {
  summary: string;
  id: string;
  title: string;
}

interface Summaries {
  type: 'summaries';
  summaries: Summary[];
  latency: {
    llm: number;
    metadata: number;
    parsing: number;
    summarization: number;
    total: number;
  };
}

interface Message {
  type: 'message';
  message: string;
  latency: {
    llm: number;
    total: number;
  };
}

type StreamResponse = Title | Summaries | Message;

export function PaperScout() {
  const [papers, setPapers] = useState<Array<{ title: string; url: string }>>([]);
  const [summaries, setSummaries] = useState<Array<{ summary: string; id: string; title: string }>>([]);
  const [currentStatus, setCurrentStatus] = useState<string>("");
  const [currentLatency, setCurrentLatency] = useState<number>(0);
  const [isLoading, setIsLoading] = useState(false);
  const [currentTool, setCurrentTool] = useState<string>("");
  const [maxResults, setMaxResults] = useState<number>(3);
  const [error, setError] = useState<string>("");
  const [queryHistory, setQueryHistory] = useState<Array<{ query: string; timestamp: string }>>([]);
  const [query, setQuery] = useState<string>("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;

    setIsLoading(true);
    setError("");
    setPapers([]);
    setSummaries([]);
    setCurrentStatus("");
    setCurrentLatency(0);
    setCurrentTool("");

    // Add to query history
    setQueryHistory(prev => [{
      query: query,
      timestamp: new Date().toLocaleTimeString()
    }, ...prev]);

    try {
      const response = await fetch("http://localhost:8000/stream", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: query, max_results: maxResults }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const reader = response.body?.getReader();
      if (!reader) throw new Error("No reader available");

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const text = new TextDecoder().decode(value);
        const lines = text.split("\n").filter(Boolean);

        for (const line of lines) {
          const data = JSON.parse(line);
          
          switch (data.type) {
            case "status":
              setCurrentStatus(data.status);
              setCurrentLatency(data.latency);
              break;
            case "titles":
              setPapers(data.papers);
              break;
            case "summaries":
              setSummaries(data.summaries);
              setCurrentStatus("");
              setCurrentLatency(0);
              break;
            case "message":
              setError(data.message);
              break;
          }
        }
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "An error occurred");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Container size="md" py="xl" style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
      <Paper shadow="sm" p="xl" radius="md" withBorder style={{ flex: 1, display: 'flex', flexDirection: 'column', width: '100%', maxWidth: '800px' }}>
        <Stack gap="md" style={{ flex: 1 }}>
          <Title order={2} style={{ color: '#000000', textAlign: 'center' }}>PaperScout</Title>

          <div style={{ flex: 1, display: 'flex', flexDirection: 'column', justifyContent: 'center', alignItems: 'center' }}>
            <form onSubmit={handleSubmit} style={{ width: '100%', maxWidth: '600px' }}>
              <Stack gap="md" align="center">
                <Group align="flex-end" style={{ width: '100%', justifyContent: 'center' }}>
                  <TextInput
                    placeholder="Ask about papers..."
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    disabled={isLoading}
                    size="md"
                    style={{ width: '400px' }}
                    styles={{
                      input: { color: '#000000', backgroundColor: '#ffffff' }
                    }}
                  />
                  <NumberInput
                    label="Max Results"
                    value={maxResults}
                    onChange={(val) => setMaxResults(Number(val) || 3)}
                    min={1}
                    max={10}
                    size="xs"
                    w={100}
                    styles={{
                      label: { color: '#000000' },
                      input: { color: '#000000', backgroundColor: '#ffffff' }
                    }}
                  />
                </Group>
                <Button type="submit" loading={isLoading} size="md" style={{ width: '200px' }}>
                  Search
                </Button>
              </Stack>
            </form>

            {currentStatus && (
              <Text size="sm" style={{ color: '#666666', textAlign: 'center', marginTop: '1rem' }}>
                {currentStatus}
              </Text>
            )}
          </div>

          {error && (
            <Alert color="red" title="Error" style={{ maxWidth: '600px', margin: '0 auto' }}>
              {error}
            </Alert>
          )}

          {papers.length > 0 && (
            <Stack gap="xs">
              <Title order={3} size="h4" style={{ color: '#000000' }}>Found Papers</Title>
              {papers.map((paper, index) => (
                <Paper key={index} p="xs" withBorder>
                  <Group gap="xs">
                    <Image src="/arxiv-logo.png" width={32} height={32} alt="arXiv Logo" />
                    <Text size="sm">
                      <a href={paper.url} target="_blank" rel="noopener noreferrer" style={{ color: '#000000' }}>
                        {paper.title}
                      </a>
                    </Text>
                  </Group>
                </Paper>
              ))}
            </Stack>
          )}

          {summaries.length > 0 && (
            <Stack gap="xs">
              <Title order={3} size="h4" style={{ color: '#000000' }}>Summaries</Title>
              {summaries.map((summary, index) => (
                <Paper key={summary.id} p="md" withBorder>
                  <Title order={4} size="h5" style={{ color: '#000000' }} mb="xs">{summary.title}</Title>
                  <div style={{ color: '#000000' }}>
                    <ReactMarkdown>{summary.summary}</ReactMarkdown>
                  </div>
                </Paper>
              ))}
            </Stack>
          )}

          {queryHistory.length > 0 && (
            <Stack gap="xs">
              <Title order={3} size="h4" style={{ color: '#000000' }}>Query History</Title>
              {queryHistory.map((item, index) => (
                <Paper key={index} p="xs" withBorder>
                  <Text size="sm" style={{ color: '#000000' }}>{item.query}</Text>
                </Paper>
              ))}
            </Stack>
          )}
        </Stack>
      </Paper>
    </Container>
  );
} 