// ASHFALL — ATemporalProp implementation.
#include "TemporalProp.h"
#include "TemporalStateComponent.h"

ATemporalProp::ATemporalProp()
{
	Temporal = CreateDefaultSubobject<UTemporalStateComponent>(TEXT("Temporal"));

	// Static-mesh actors are static-mobility by default; temporal props move and
	// swap materials at runtime, so they must be movable.
	if (UStaticMeshComponent* Mesh = GetStaticMeshComponent())
	{
		Mesh->SetMobility(EComponentMobility::Movable);
	}
}
