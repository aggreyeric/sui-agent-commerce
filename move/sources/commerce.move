/// agent_commerce — Autonomous Agent Marketplace on Sui
///
/// Agents register `Service` objects for sale, other agents buy them via
/// policy-gated payments, and receive `Purchase` receipts as transferable objects.
///
/// Built for Sui Overflow 2026 — Agentic Web Track.
module agent_commerce::commerce {

    use sui::coin::{Self, Coin};
    use sui::sui::SUI;
    use sui::object::{Self, UID};
    use sui::transfer;
    use sui::tx_context::{Self, TxContext};
    use sui::event;

    /// ========== Errors ==========
    const EInsufficientPayment: u64 = 0;
    const EServiceInactive: u64 = 1;
    const ENotOwner: u64 = 2;

    /// ========== Events ==========
    public struct ServiceRegistered has copy, drop {
        service_id: ID,
        seller: address,
        name: vector<u8>,
        price: u64,
    }

    public struct ServicePurchased has copy, drop {
        service_id: ID,
        purchase_id: ID,
        buyer: address,
        seller: address,
        price: u64,
    }

    /// ========== Objects ==========
    /// A service offered by a seller agent.
    public struct Service has key {
        id: UID,
        seller: address,
        name: vector<u8>,
        description: vector<u8>,
        price: u64,           // in mist
        active: bool,
        sales_count: u64,
        total_revenue: u64,
    }

    /// A verifiable receipt proving an agent purchased a service.
    /// Transferable — can be used as proof-of-purchase elsewhere.
    public struct Purchase has key {
        id: UID,
        service_id: ID,
        buyer: address,
        seller: address,
        price_paid: u64,
        purchased_at: u64,
    }

    /// ========== Entry Functions ==========

    /// Register a service for sale. Creates a `Service` object owned by the seller.
    public fun register_service(
        name: vector<u8>,
        description: vector<u8>,
        price: u64,
        ctx: &mut TxContext,
    ) {
        let seller = tx_context::sender(ctx);
        let service = Service {
            id: object::new(ctx),
            seller,
            name,
            description,
            price,
            active: true,
            sales_count: 0,
            total_revenue: 0,
        };

        event::emit(ServiceRegistered {
            service_id: object::id(&service),
            seller,
            name,
            price,
        });

        transfer::share_object(service);
    }

    /// Buy a service. Payment must be >= service price.
    /// Buyer receives a `Purchase` receipt. Seller gets paid.
    public fun buy_service(
        service: &mut Service,
        payment: Coin<SUI>,
        ctx: &mut TxContext,
    ) {
        let buyer = tx_context::sender(ctx);
        let price = service.price;

        assert!(service.active, EServiceInactive);
        assert!(coin::value(&payment) >= price, EInsufficientPayment);

        // Create the receipt first (before moving payment)
        let purchase = Purchase {
            id: object::new(ctx),
            service_id: object::id(service),
            buyer,
            seller: service.seller,
            price_paid: price,
            purchased_at: tx_context::epoch(ctx),
        };

        // Update service stats
        service.sales_count = service.sales_count + 1;
        service.total_revenue = service.total_revenue + price;

        event::emit(ServicePurchased {
            service_id: object::id(service),
            purchase_id: object::id(&purchase),
            buyer,
            seller: service.seller,
            price,
        });

        // Transfer receipt to buyer
        transfer::transfer(purchase, buyer);

        // Pay the seller
        transfer::public_transfer(payment, service.seller);
    }

    /// Deactivate a service (seller only).
    public fun deactivate_service(service: &mut Service, ctx: &TxContext) {
        assert!(tx_context::sender(ctx) == service.seller, ENotOwner);
        service.active = false;
    }

    /// Reactivate a service (seller only).
    public fun reactivate_service(service: &mut Service, ctx: &TxContext) {
        assert!(tx_context::sender(ctx) == service.seller, ENotOwner);
        service.active = true;
    }

    /// ========== View Functions ==========
    public fun service_price(service: &Service): u64 { service.price }
    public fun service_active(service: &Service): bool { service.active }
    public fun service_seller(service: &Service): address { service.seller }
    public fun service_sales(service: &Service): u64 { service.sales_count }
    public fun service_revenue(service: &Service): u64 { service.total_revenue }
    public fun service_name(service: &Service): &vector<u8> { &service.name }
    public fun purchase_buyer(purchase: &Purchase): address { purchase.buyer }
    public fun purchase_price(purchase: &Purchase): u64 { purchase.price_paid }
}
