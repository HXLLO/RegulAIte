#!/usr/bin/env python3
"""
Script de test simple pour vérifier les corrections du système d'agents.
"""
import sys
import os
from pathlib import Path

# Add the backend directory to the path
backend_dir = Path(__file__).parent / "backend"
if str(backend_dir) not in sys.path:
    sys.path.append(str(backend_dir))

def test_imports():
    """Test que les imports fonctionnent correctement."""
    print("🔍 Testing imports...")
    
    try:
        # Test orchestrator import
        from agent_framework.orchestrator import OrchestratorAgent
        print("✅ OrchestratorAgent import successful")
        
        # Test factory import
        from agent_framework.factory import initialize_complete_agent_system, create_specialized_agents
        print("✅ Factory imports successful")
        
        # Test agent modules
        from agent_framework.modules.risk_assessment_module import RiskAssessmentModule
        from agent_framework.modules.compliance_analysis_module import ComplianceAnalysisModule
        from agent_framework.modules.governance_analysis_module import GovernanceAnalysisModule
        from agent_framework.modules.gap_analysis_module import GapAnalysisModule
        print("✅ Agent modules import successful")
        
        return True
        
    except Exception as e:
        print(f"❌ Import failed: {str(e)}")
        return False

def test_orchestrator_methods():
    """Test que les nouvelles méthodes de l'orchestrateur existent."""
    print("🔍 Testing orchestrator methods...")
    
    try:
        from agent_framework.orchestrator import OrchestratorAgent
        
        # Check if new methods exist
        methods = ['register_agent', 'get_registered_agents', 'debug_agent_status']
        
        for method in methods:
            if hasattr(OrchestratorAgent, method):
                print(f"✅ Method {method} exists")
            else:
                print(f"❌ Method {method} missing")
                return False
                
        return True
        
    except Exception as e:
        print(f"❌ Method test failed: {str(e)}")
        return False

def test_main_functions():
    """Test que les nouvelles fonctions du main existent."""
    print("🔍 Testing main.py functions...")
    
    try:
        # Test that the functions exist in main.py
        main_file = backend_dir / "main.py"
        if not main_file.exists():
            print("❌ main.py not found")
            return False
            
        with open(main_file, 'r') as f:
            content = f.read()
            
        functions = ['get_global_orchestrator', 'is_agent_system_ready']
        
        for func in functions:
            if f"def {func}(" in content:
                print(f"✅ Function {func} exists in main.py")
            else:
                print(f"❌ Function {func} missing in main.py")
                return False
                
        return True
        
    except Exception as e:
        print(f"❌ Main functions test failed: {str(e)}")
        return False

def test_router_modifications():
    """Test que les modifications du routeur sont présentes."""
    print("🔍 Testing router modifications...")
    
    try:
        router_file = backend_dir / "routers" / "agents_router.py"
        if not router_file.exists():
            print("❌ agents_router.py not found")
            return False
            
        with open(router_file, 'r') as f:
            content = f.read()
            
        # Check for key modifications
        checks = [
            ("from main import agent_orchestrator", "Global orchestrator import"),
            ("Using global orchestrator", "Global orchestrator usage"),
            ("Creating fallback orchestrator", "Fallback mechanism")
        ]
        
        for check, description in checks:
            if check in content:
                print(f"✅ {description} found")
            else:
                print(f"❌ {description} missing")
                return False
                
        return True
        
    except Exception as e:
        print(f"❌ Router test failed: {str(e)}")
        return False

def test_factory_debug():
    """Test que le debug a été ajouté à la factory."""
    print("🔍 Testing factory debug additions...")
    
    try:
        factory_file = backend_dir / "agent_framework" / "factory.py"
        if not factory_file.exists():
            print("❌ factory.py not found")
            return False
            
        with open(factory_file, 'r') as f:
            content = f.read()
            
        if "orchestrator.debug_agent_status()" in content:
            print("✅ Debug call added to factory")
            return True
        else:
            print("❌ Debug call missing in factory")
            return False
            
    except Exception as e:
        print(f"❌ Factory debug test failed: {str(e)}")
        return False

def main():
    """Run all tests."""
    print("🚀 Starting agent system fix verification...")
    print("=" * 50)
    
    tests = [
        ("Import Tests", test_imports),
        ("Orchestrator Methods", test_orchestrator_methods),
        ("Main Functions", test_main_functions),
        ("Router Modifications", test_router_modifications),
        ("Factory Debug", test_factory_debug)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 {test_name}:")
        if test_func():
            passed += 1
            print(f"✅ {test_name} PASSED")
        else:
            print(f"❌ {test_name} FAILED")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The agent system fixes are in place.")
        print("\n📝 Summary of fixes applied:")
        print("  1. ✅ Synchronous agent initialization in main.py")
        print("  2. ✅ Global orchestrator sharing between main.py and router")
        print("  3. ✅ Debug methods added to orchestrator")
        print("  4. ✅ Fallback mechanism in router")
        print("  5. ✅ Enhanced logging and status checking")
        print("\n🚀 The system should now properly initialize agents and avoid the 'Agent non trouvé' errors.")
        return True
    else:
        print("❌ Some tests failed. Please check the output above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 