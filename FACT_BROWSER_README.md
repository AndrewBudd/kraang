# Kraang Fact Browser

A client-side web interface for browsing the Kraang knowledge base.

## Usage

Simply open the HTML file in your browser:

```bash
# From the kraang directory
open fact-browser.html        # macOS
xdg-open fact-browser.html    # Linux
start fact-browser.html        # Windows
```

Or drag and drop `fact-browser.html` into your browser.

## Features

### Search & Filter
- **Search**: Real-time text search across all fact statements
- **Type Filter**: Filter by fact type (implementation, constraint, requirement, design, threat_vector)
- **Artifact Filter**: Show facts from specific files
- **Confidence Filter**: Filter by confidence level (high/medium/low)

### View Modes
- **Detailed**: Full fact information including sources and metadata
- **Compact**: Condensed view for quick scanning

### Display
- **Color-coded types**: Each fact type has a distinct color
- **Confidence bars**: Visual representation of fact confidence (0-100%)
- **Source tracking**: See which files each fact was extracted from
- **Live stats**: Total facts, filtered count, total artifacts

## Technical Details

- **Pure client-side**: No server required, works offline
- **Reads from**: `.kraang/facts.json` and `.kraang/artifacts.json`
- **Fast filtering**: All processing happens in-browser
- **Responsive**: Works on desktop and mobile

## Requirements

- Modern web browser (Chrome, Firefox, Safari, Edge)
- Must be opened from the kraang directory (so it can access `.kraang/` files)

## Troubleshooting

**"Error Loading Data"**
- Make sure you're opening the file from the `/home/budda/Code/kraang` directory
- Check that `.kraang/facts.json` exists and is readable
- Some browsers block file:// access - try Firefox or run a local server:
  ```bash
  python3 -m http.server 8000
  # Then visit: http://localhost:8000/fact-browser.html
  ```

**No facts showing**
- Check your filters - try resetting them to "All"
- Clear the search box

## Color Legend

- **Green** (Implementation): Code implementations and patterns
- **Red** (Constraint): Rules and restrictions
- **Blue** (Requirement): Requirements and specifications
- **Yellow** (Design): Design decisions and patterns
- **Purple** (Threat Vector): Security threats

## Tips

1. Use search for quick lookup: "malloc", "Docker", "memory"
2. Filter by artifact to see all facts from one file
3. Use compact view when scanning many facts
4. Confidence bars show extraction quality (green = high confidence)
5. Click sources to see where facts came from

## Browser Compatibility

Works in all modern browsers:
- ✅ Chrome/Edge (recommended)
- ✅ Firefox
- ✅ Safari
- ✅ Brave

## Future Enhancements

Potential additions:
- Relationship visualization
- Conflict highlighting
- Export filtered results
- Bookmark/favorite facts
- Dark/light theme toggle
- Sort options
