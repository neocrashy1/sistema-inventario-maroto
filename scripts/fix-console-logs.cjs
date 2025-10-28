#!/usr/bin/env node
const fs = require('fs')
const path = require('path')
const glob = require('glob')

const ROOT = path.resolve(__dirname, '..')
const patterns = [
  'src/**/*.js',
  'src/**/*.ts',
  'src/**/*.vue'
]

const exclude = [/node_modules/, /dist\//, /\/tests?\//, /\.test\./, /\.spec\./]

function shouldExclude(file) {
  return exclude.some(re => re.test(file))
}

function hasLoggerImport(content) {
  return /import\s+logger\s+from\s+['\"]@\/utils\/logger['\"]/m.test(content) || /const\s+logger\s*=\s*require\(['\"]@\/utils\/logger['\"]\)/m.test(content)
}

function addLoggerImportForVue(content) {
  // Handle <script setup> or <script>
  if (/<script\s+setup/.test(content)) {
    return content.replace(/<script\s+setup([^>]*)>/, (m, p1) => `${m}\nimport logger from '@/utils/logger'`)
  }
  if (/<script[^>]*>/.test(content)) {
    return content.replace(/<script([^>]*)>/, (m, p1) => `${m}\nimport logger from '@/utils/logger'`)
  }
  // fallback - prepend at top
  return `import logger from '@/utils/logger'\n${content}`
}

function addLoggerImportForJs(content) {
  // If file seems ESM (has import/export), add import at top after existing header comments
  if (/^\s*\/\//.test(content) || /^\s*\/\*/.test(content)) {
    // insert after first comment block or at top
    const lines = content.split(/\r?\n/)
    let insertAt = 0
    for (let i = 0; i < Math.min(10, lines.length); i++) {
      if (!lines[i].startsWith('//') && !lines[i].startsWith('/*') && lines[i].trim() !== '') { insertAt = i; break }
      insertAt = i+1
    }
    lines.splice(insertAt, 0, "import logger from '@/utils/logger'")
    return lines.join('\n')
  }
  // simple prepend
  return `import logger from '@/utils/logger'\n${content}`
}

function replaceLogs(content) {
  // Replace console.* calls
  content = content.replace(/console\.error\s*\(/g, 'logger.error(')
  content = content.replace(/console\.warn\s*\(/g, 'logger.warn(')
  content = content.replace(/console\.log\s*\(/g, 'logger.debug(')
  return content
}

let changedFiles = []
for (const pattern of patterns) {
  const files = glob.sync(pattern, { cwd: ROOT, absolute: true })
  for (const file of files) {
    const rel = path.relative(ROOT, file).replace(/\\/g, '/')
    if (shouldExclude(rel)) continue
    try {
      let content = fs.readFileSync(file, 'utf8')
      if (!/console\.log|console\.error|console\.warn/.test(content)) continue

      let original = content
      let addedImport = false
      if (!hasLoggerImport(content)) {
        if (file.endsWith('.vue')) {
          content = addLoggerImportForVue(content)
        } else {
          content = addLoggerImportForJs(content)
        }
        addedImport = true
      }

      content = replaceLogs(content)

      if (content !== original) {
        // backup
        fs.writeFileSync(file + '.bak', original, 'utf8')
        fs.writeFileSync(file, content, 'utf8')
        changedFiles.push({ file: rel, importAdded: addedImport })
      }
    } catch (err) {
      console.error('Failed to process', file, err.message)
    }
  }
}

console.log('Files changed:', changedFiles.length)
changedFiles.forEach(f => console.log(' -', f.file, f.importAdded ? '(import added)' : ''))

process.exit(0)
