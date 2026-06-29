// ASHFALL — UAshfallTemporalLibrary implementation.
#include "AshfallTemporalLibrary.h"
#include "TemporalSubsystem.h"
#include "Engine/Engine.h"
#include "Engine/World.h"

UTemporalSubsystem* UAshfallTemporalLibrary::GetTemporalSubsystem(const UObject* WorldContextObject)
{
	if (!GEngine || !WorldContextObject)
	{
		return nullptr;
	}
	if (UWorld* World = GEngine->GetWorldFromContextObject(WorldContextObject, EGetWorldErrorMode::LogAndReturnNull))
	{
		return World->GetSubsystem<UTemporalSubsystem>();
	}
	return nullptr;
}

ETimeState UAshfallTemporalLibrary::ToggleTimeState(const UObject* WorldContextObject)
{
	if (UTemporalSubsystem* Subsystem = GetTemporalSubsystem(WorldContextObject))
	{
		Subsystem->RequestToggle();
		return Subsystem->GetState();
	}
	return ETimeState::Zenith;
}

ETimeState UAshfallTemporalLibrary::GetTimeState(const UObject* WorldContextObject)
{
	if (const UTemporalSubsystem* Subsystem = GetTemporalSubsystem(WorldContextObject))
	{
		return Subsystem->GetState();
	}
	return ETimeState::Zenith;
}

void UAshfallTemporalLibrary::SetTimeState(const UObject* WorldContextObject, ETimeState NewState)
{
	if (UTemporalSubsystem* Subsystem = GetTemporalSubsystem(WorldContextObject))
	{
		Subsystem->SetState(NewState);
	}
}

void UAshfallTemporalLibrary::SetCausalFlag(const UObject* WorldContextObject, FName Flag, bool bSet)
{
	if (UTemporalSubsystem* Subsystem = GetTemporalSubsystem(WorldContextObject))
	{
		Subsystem->SetCausalFlag(Flag, bSet);
	}
}

bool UAshfallTemporalLibrary::HasCausalFlag(const UObject* WorldContextObject, FName Flag)
{
	if (const UTemporalSubsystem* Subsystem = GetTemporalSubsystem(WorldContextObject))
	{
		return Subsystem->HasCausalFlag(Flag);
	}
	return false;
}
