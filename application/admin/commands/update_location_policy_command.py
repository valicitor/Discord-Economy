from attr import dataclass
from infrastructure import LocationPolicyRepository
from domain import LocationPolicy, RecordNotFoundException, UpdateFailedException


@dataclass
class UpdateLocationPolicyCommandRequest:
    location_id: int
    tax_rate: float | None = None
    trade_tariff: float | None = None
    import_restricted: bool | None = None
    export_restricted: bool | None = None
    interest_rate_modifier: float | None = None
    smuggling_risk_modifier: float | None = None


@dataclass
class UpdateLocationPolicyCommandResponse:
    success: bool
    policy: LocationPolicy


class UpdateLocationPolicyCommand:

    def __init__(self, request: UpdateLocationPolicyCommandRequest):
        self.request = request

    async def execute(self) -> UpdateLocationPolicyCommandResponse:
        repo = await LocationPolicyRepository().get_instance()

        policy = await repo.get_by_location(self.request.location_id)
        if not policy:
            raise RecordNotFoundException(f"No policy found for location {self.request.location_id}.")

        if self.request.tax_rate is not None:
            policy.tax_rate = self.request.tax_rate
        if self.request.trade_tariff is not None:
            policy.trade_tariff = self.request.trade_tariff
        if self.request.import_restricted is not None:
            policy.import_restricted = self.request.import_restricted
        if self.request.export_restricted is not None:
            policy.export_restricted = self.request.export_restricted
        if self.request.interest_rate_modifier is not None:
            policy.interest_rate_modifier = self.request.interest_rate_modifier
        if self.request.smuggling_risk_modifier is not None:
            policy.smuggling_risk_modifier = self.request.smuggling_risk_modifier

        updated = await repo.update(policy)
        if not updated:
            raise UpdateFailedException("Failed to update location policy.")

        return UpdateLocationPolicyCommandResponse(success=True, policy=policy)
