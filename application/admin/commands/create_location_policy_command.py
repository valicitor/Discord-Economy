from attr import dataclass
from infrastructure import LocationPolicyRepository, LocationRepository
from domain import LocationPolicy, CreateFailedException, RecordNotFoundException, DuplicateRecordException


@dataclass
class CreateLocationPolicyCommandRequest:
    location_id: int
    tax_rate: float = 0.0
    trade_tariff: float = 0.0
    import_restricted: bool = False
    export_restricted: bool = False
    interest_rate_modifier: float = 1.0
    smuggling_risk_modifier: float = 1.0


@dataclass
class CreateLocationPolicyCommandResponse:
    success: bool
    policy: LocationPolicy


class CreateLocationPolicyCommand:

    def __init__(self, request: CreateLocationPolicyCommandRequest):
        self.request = request

    async def execute(self) -> CreateLocationPolicyCommandResponse:
        location_repo = await LocationRepository().get_instance()
        policy_repo = await LocationPolicyRepository().get_instance()

        location = await location_repo.get_by_id(self.request.location_id)
        if not location:
            raise RecordNotFoundException(f"Location {self.request.location_id} not found.")

        if await policy_repo.exists(self.request.location_id):
            raise DuplicateRecordException(f"Location {self.request.location_id} already has a policy. Use edit to update it.")

        policy = LocationPolicy(
            location_id=self.request.location_id,
            tax_rate=self.request.tax_rate,
            trade_tariff=self.request.trade_tariff,
            import_restricted=self.request.import_restricted,
            export_restricted=self.request.export_restricted,
            interest_rate_modifier=self.request.interest_rate_modifier,
            smuggling_risk_modifier=self.request.smuggling_risk_modifier,
        )
        policy_id = await policy_repo.insert(policy)
        if not policy_id:
            raise CreateFailedException("Failed to create location policy.")

        policy.policy_id = policy_id
        return CreateLocationPolicyCommandResponse(success=True, policy=policy)
