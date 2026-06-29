// ASHFALL — AAshfallCharacter implementation.
#include "AshfallCharacter.h"
#include "TemporalControlComponent.h"

AAshfallCharacter::AAshfallCharacter()
{
	TemporalControl = CreateDefaultSubobject<UTemporalControlComponent>(TEXT("TemporalControl"));
}
