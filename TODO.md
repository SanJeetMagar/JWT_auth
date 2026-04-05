# JWT_auth Profile Endpoint Update

## Steps:

- [x] 1. Create UserProfileSerializer in serializers.py nesting user fields (username, fullname=name, email) + profile fields.
- [ ] 2. Update views.py: Import UserProfileSerializer, replace ProfileSerializer with UserProfileSerializer in ProfileView (GET/PATCH), update @extend_schema.
- [ ] 3. Test endpoint.

Current status: Step 2 complete. Proceeding to step 3 (testing).
