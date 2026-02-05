# Contributing to ClawFarm

ClawFarm is an agent-first repository demonstrating automated workflows. Contributions welcome!

## Philosophy

This project follows **agent-first development** principles:

1. **Self-documenting** - Code should be clear without comments
2. **No manual steps** - Everything should be automated
3. **Clear structure** - Files organized by purpose
4. **Reproducible** - Should work anywhere with API keys

## Repository Structure

```
clawfarm/
├── lib/          # Shared utilities (keep DRY)
├── leonardo/     # Leonardo.ai specific code
├── mosaic/       # Mosaic generation code  
├── clawcon/      # Claw-Con voting code
├── examples/     # Usage examples & guides
└── results/      # Output directory (gitignored)
```

**Rules:**
- Keep modules independent (don't cross-import between leonardo/mosaic/clawcon)
- Shared code goes in `lib/`
- Each module has its own README
- All scripts executable from workspace root

## Adding New Modules

1. Create directory: `mkdir mymodule/`
2. Add README: `mymodule/README.md`
3. Add scripts with proper imports: `from lib.agentmail_utils import ...`
4. Update main README.md with module description

## Code Style

- **Python 3.12+** with type hints encouraged
- **async/await** for I/O operations
- **httpx** for HTTP (not requests)
- **Descriptive names** over comments
- **Early returns** over nested if/else

## Testing

No formal test suite (yet), but:
- Test with small counts first (e.g., `--count 3`)
- Check success rates in output
- Verify results JSON files

## Documentation

- Update relevant README when changing functionality
- Add examples to `examples/` for new features
- Keep main README.md up to date

## Pull Requests

1. Fork the repo
2. Create feature branch
3. Make changes
4. Test locally
5. Update docs
6. Submit PR with clear description

## Issues

Report bugs or suggest features via GitHub Issues:
- Include error messages
- Share relevant JSON results (redact API keys!)
- Describe expected vs actual behavior

## License

By contributing, you agree to license your contributions under MIT.

## Questions?

Open an issue or join the discussion on Discord.
