// ASHFALL — UTemporalControlComponent implementation.
#include "TemporalControlComponent.h"
#include "TemporalSubsystem.h"
#include "Engine/World.h"

UTemporalControlComponent::UTemporalControlComponent()
{
	PrimaryComponentTick.bCanEverTick = false;
}

UTemporalSubsystem* UTemporalControlComponent::GetSubsystem() const
{
	if (const UWorld* World = GetWorld())
	{
		return World->GetSubsystem<UTemporalSubsystem>();
	}
	return nullptr;
}

bool UTemporalControlComponent::RequestToggle()
{
	UTemporalSubsystem* Subsystem = GetSubsystem();
	if (!Subsystem)
	{
		return false;
	}

	const UWorld* World = GetWorld();
	const double Now = World ? World->GetTimeSeconds() : 0.0;
	if (Now - LastToggleTime < ToggleCooldown)
	{
		return false;
	}

	LastToggleTime = Now;
	Subsystem->RequestToggle();
	return true;
}

ETimeState UTemporalControlComponent::GetState() const
{
	const UTemporalSubsystem* Subsystem = GetSubsystem();
	return Subsystem ? Subsystem->GetState() : ETimeState::Zenith;
}
