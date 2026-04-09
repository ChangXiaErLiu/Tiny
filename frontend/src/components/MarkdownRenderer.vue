<template>
  <div class="markdown-content" v-html="renderedContent"></div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { marked } from 'marked'
import hljs from 'highlight.js/lib/core'
import javascript from 'highlight.js/lib/languages/javascript'
import typescript from 'highlight.js/lib/languages/typescript'
import python from 'highlight.js/lib/languages/python'
import json from 'highlight.js/lib/languages/json'
import bash from 'highlight.js/lib/languages/bash'

hljs.registerLanguage('javascript', javascript)
hljs.registerLanguage('typescript', typescript)
hljs.registerLanguage('python', python)
hljs.registerLanguage('json', json)
hljs.registerLanguage('bash', bash)
hljs.registerLanguage('js', javascript)
hljs.registerLanguage('ts', typescript)
hljs.registerLanguage('py', python)

marked.setOptions({
  gfm: true,
  breaks: true
})

const props = defineProps<{
  content: string
}>()

const renderMarkdown = (text: string): string => {
  let result = text

  result = result.replace(/```(\w+)?\n([\s\S]*?)```/g, (_, lang, code) => {
    const language = lang || 'plaintext'
    let highlighted = code.trim()
    try {
      if (hljs.getLanguage(language)) {
        highlighted = hljs.highlight(code.trim(), { language }).value
      } else {
        highlighted = hljs.highlightAuto(code.trim()).value
      }
    } catch (e) {
      // fallback
    }
    return `<pre class="code-block"><code class="hljs language-${language}">${highlighted}</code></pre>`
  })

  result = result.replace(/`([^`]+)`/g, '<code class="inline-code">$1</code>')

  result = result.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>')
  result = result.replace(/\*([^*]+)\*/g, '<em>$1</em>')

  result = result.replace(/^### (.+)$/gm, '<h3>$1</h3>')
  result = result.replace(/^## (.+)$/gm, '<h2>$1</h2>')
  result = result.replace(/^# (.+)$/gm, '<h1>$1</h1>')

  result = result.replace(/^\- (.+)$/gm, '<li>$1</li>')
  result = result.replace(/(<li>.*<\/li>\n?)+/g, '<ul>$&</ul>')

  result = result.replace(/^\d+\. (.+)$/gm, '<li>$1</li>')

  result = result.replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank" rel="noopener">$1</a>')

  result = result.replace(/\|(.+)\|/g, (match) => {
    const cells = match.split('|').filter(c => c.trim())
    if (cells.every(c => c.trim().match(/^-+$/))) {
      return ''
    }
    const row = cells.map(c => `<td>${c.trim()}</td>`).join('')
    return `<tr>${row}</tr>`
  })

  result = result.replace(/(<tr>.*<\/tr>\n?)+/g, '<table>$&</table>')

  result = result.replace(/\n\n/g, '</p><p>')
  result = result.replace(/\n/g, '<br>')

  if (!result.startsWith('<')) {
    result = '<p>' + result + '</p>'
  }

  return result
}

const renderedContent = computed(() => {
  if (!props.content) return ''
  return renderMarkdown(props.content)
})
</script>

<style scoped>
.markdown-content {
  line-height: 1.7;
  font-size: 14px;
  color: inherit;
}

.markdown-content :deep(h1) {
  font-size: 1.5em;
  font-weight: 700;
  margin: 0.5em 0;
  color: #1a1a2e;
}

.markdown-content :deep(h2) {
  font-size: 1.3em;
  font-weight: 600;
  margin: 0.5em 0;
  color: #1a1a2e;
}

.markdown-content :deep(h3) {
  font-size: 1.1em;
  font-weight: 600;
  margin: 0.5em 0;
  color: #1a1a2e;
}

.markdown-content :deep(p) {
  margin: 0.5em 0;
}

.markdown-content :deep(ul),
.markdown-content :deep(ol) {
  margin: 0.5em 0;
  padding-left: 1.5em;
}

.markdown-content :deep(li) {
  margin: 0.25em 0;
}

.markdown-content :deep(strong) {
  font-weight: 600;
  color: #1a1a2e;
}

.markdown-content :deep(em) {
  font-style: italic;
}

.markdown-content :deep(a) {
  color: #6366f1;
  text-decoration: none;
}

.markdown-content :deep(a:hover) {
  text-decoration: underline;
}

.markdown-content :deep(.inline-code) {
  background: rgba(0, 0, 0, 0.06);
  padding: 0.15em 0.4em;
  border-radius: 4px;
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.9em;
  color: #e11d48;
}

.markdown-content :deep(.code-block) {
  background: #1e1e2e;
  border-radius: 8px;
  padding: 12px 16px;
  margin: 0.75em 0;
  overflow-x: auto;
  font-size: 0.85em;
}

.markdown-content :deep(.code-block code) {
  font-family: 'JetBrains Mono', monospace;
  color: #cdd6f4;
  background: none;
  padding: 0;
}

.markdown-content :deep(table) {
  border-collapse: collapse;
  margin: 0.75em 0;
  width: 100%;
  font-size: 0.9em;
}

.markdown-content :deep(td),
.markdown-content :deep(th) {
  border: 1px solid #e5e7eb;
  padding: 8px 12px;
  text-align: left;
}

.markdown-content :deep(th) {
  background: rgba(0, 0, 0, 0.03);
  font-weight: 600;
}

.markdown-content :deep(tr:hover) {
  background: rgba(0, 0, 0, 0.02);
}
</style>
