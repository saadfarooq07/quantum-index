# Warp terminal integration for command suggestions
WARP_QUANTUM_COMMANDS=(
'qcheck:Check quantum-index status for a repository'
'qclean:Clean quantum-index data for a repository'
'qnap:Generate quantum-index snapshots'
'qterm:Interactive quantum terminal with ML assistance'
)

# Register commands with Warp if it's available
if [[ -n "$WARP_IS_LOCAL_SHELL_SESSION" ]]; then
for cmd in $WARP_QUANTUM_COMMANDS; do
    local command_name="${cmd%%:*}"
    local description="${cmd#*:}"
    
    # Register command suggestion
    command_metadata+="{\"name\":\"$command_name\",\"description\":\"$description\"}"
done
fi

