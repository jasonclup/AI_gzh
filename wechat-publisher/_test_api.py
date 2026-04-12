"""Quick Flask route test - output goes to file for inspection."""
import sys, os, traceback, json

sys.path.insert(0, os.path.dirname(__file__))

result_file = os.path.join(os.path.dirname(__file__), '_test_result.txt')

try:
    from web.app import create_app
    import yaml
    with open('config.yaml', 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    app = create_app(config)
    
    with app.test_client() as client:
        r = client.get('/api/topics/fetch')
        d = r.get_json()
        
        with open(result_file, 'w', encoding='utf-8') as f:
            f.write(f"STATUS={d.get('success')}\n")
            f.write(f"COUNT={len(d.get('data', []))}\n")
            if d.get('data'):
                f.write(f"SOURCE={d['data'][0].get('source','?')}\n")
                f.write(f"TITLE={d['data'][0].get('title','?')[:30]}\n")
            else:
                f.write("NO_DATA\n")
        print("TEST_DONE")

except Exception as e:
    with open(result_file, 'w', encoding='utf-8') as f:
        f.write(f"ERROR: {e}\n")
        f.write(traceback.format_exc())
    print("TEST_FAIL")
