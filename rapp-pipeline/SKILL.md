---
name: "rapp-pipeline"
description: "Run RAPP (Rapid Agent Prototyping Platform) pipeline to generate AI agents from transcripts. Use when building agents, generating Copilot Studio solutions, or deploying to Microsoft AI stack."
allowed-tools: "Bash, Read, Write, Glob, Grep"
---

# RAPP Pipeline Skill

This skill runs the RAPP pipeline to generate production-ready AI agents from business transcripts.

## Available Commands

### Full Pipeline (Transcript to Agent)
```bash
python3 -m rapp_cli pipeline <project_id> [options]
```

Options:
- `-t, --transcript PATH` - Path to transcript file
- `-c, --customer TEXT` - Customer name
- `-o, --output PATH` - Output directory
- `--json-output` - Output results as JSON (for parsing)

### Copilot Studio + Azure DevOps
```bash
python3 -m rapp_cli copilot-studio <project_id> [options]
```

Options:
- `-t, --transcript PATH` - Path to transcript file
- `-c, --customer TEXT` - Customer name
- `-p, --publisher TEXT` - Solution publisher prefix
- `-e, --environments TEXT` - Target environments (comma-separated)
- `--json-output` - Output results as JSON

### Project Management
```bash
# List all projects
python3 -m rapp_cli list-projects --json-output

# Show project details
python3 -m rapp_cli show-project <project_id> --json-output

# Create new project
python3 -m rapp_cli new <project_name>
```

### Quality Gates
```bash
python3 -m rapp_cli quality-gate <project_id> --gate QG1
```

Gates: QG1 (Transcript), QG2 (Customer), QG3 (Code), QG4-QG5 (Demo), QG6 (Deployment)

### Reports
```bash
python3 -m rapp_cli report <project_id> --report-type discovery
```

Types: discovery, mvp, code, qg1-qg6, executive_summary

## Workflow

1. **Create Project**
   ```bash
   python3 -m rapp_cli new my-project
   ```

2. **Add Transcript** (save to `rapp_projects/{project}/inputs/transcript.txt`)

3. **Run Pipeline**
   ```bash
   # Basic agent generation
   python3 -m rapp_cli pipeline my-project --customer "Contoso" --json-output

   # Full Microsoft AI stack
   python3 -m rapp_cli copilot-studio my-project --customer "Contoso" --json-output
   ```

4. **Check Output**
   ```bash
   python3 -m rapp_cli show-project my-project --json-output
   ```

## Output Locations

- Agents: `rapp_projects/{project}/outputs/{agent_id}_agent.py`
- Demos: `rapp_projects/{project}/outputs/{agent_id}_demo.json`
- HTML Tester: `rapp_projects/{project}/outputs/agent_tester.html`
- Copilot Studio: `rapp_projects/{project}/copilot_studio/`
- Azure DevOps: `rapp_projects/{project}/azure_devops/`

## Working Directory

Always run commands from: `~/.rapp/src`

## Example: End-to-End Automation

```bash
cd ~/.rapp/src

# 1. Create project
python3 -m rapp_cli new contoso-agent

# 2. Create transcript (or use existing)
cat > rapp_ai/rapp_projects/contoso-agent/inputs/transcript.txt << 'EOF'
[Discovery call transcript content here]
EOF

# 3. Run full pipeline
python3 -m rapp_cli copilot-studio contoso-agent \
  --customer "Contoso Financial" \
  --publisher contoso \
  --environments "dev,test,prod" \
  --json-output

# 4. Verify outputs
python3 -m rapp_cli show-project contoso-agent --json-output
```

<!-- toaster:generated:begin -->

## Parameters

The typed contract this capability answers to (JSON Schema — the deterministic layer):

```json
{
  "properties": {
    "project_id": {
      "description": "Derived from `<project_id>` used in the documented command at line 9.",
      "type": "string"
    },
    "project_name": {
      "description": "Derived from `<project_name>` used in the documented command at line 39.",
      "type": "string"
    }
  },
  "required": [],
  "type": "object"
}
```

<!-- toaster:generated:end -->

<!-- toaster:generated:begin -->

## Deterministic steps

Lifted verbatim from the procedure above by `toaster.py toast`. Run them in order, substituting the typed parameters; do not paraphrase:

```bash
python3 -m rapp_cli pipeline <project_id> [options]
python3 -m rapp_cli copilot-studio <project_id> [options]
python3 -m rapp_cli list-projects --json-output
python3 -m rapp_cli show-project <project_id> --json-output
python3 -m rapp_cli new <project_name>
python3 -m rapp_cli quality-gate <project_id> --gate QG1
python3 -m rapp_cli report <project_id> --report-type discovery
python3 -m rapp_cli new my-project
python3 -m rapp_cli pipeline my-project --customer "Contoso" --json-output
python3 -m rapp_cli copilot-studio my-project --customer "Contoso" --json-output
python3 -m rapp_cli show-project my-project --json-output
cd ~/.rapp/src
python3 -m rapp_cli new contoso-agent
python3 -m rapp_cli copilot-studio contoso-agent \
python3 -m rapp_cli show-project contoso-agent --json-output
```

<!-- toaster:generated:end -->

<!-- rci-capsule:v1:H4sIAAAAAAAC/8V6WZOjSLLuX8GyH053U1mIRSxlM2MmgdiEALFpmRrrYhUg9h3G+v72i6TMqqye6u7qOQ8nH1IQEf65h4dv4dK/n+y2CfPq6UPWJsm7J8+vos5uojx7+vDPfz9do8x7+vBkZ5fEf3r3lESZ//SBevdU2JWdzhNFlce+2/wSefNsk1/9mezpb19G//H067vfQUG/AZPZqf8toNv4DPWvm3y1W0XFQ8Anrc0AbaWqwI+aXUQesLr4WQOoVd7kzVhE2QVQE7sJ8ir9CSiiwr9xBpocmJf5ld34wEoA7BtNDQRVngJNZWcP/Po9YNY+0Id+BjhtlHg3sMfSd6/ktyE6L6IkbwC9ab0oB+o8aW+yzYvyCvD8IsnH27KZ5y5yq7zOg+bGtG5s9/p+3qo/2GmR+PWs7Xl3YZ76xczl9TSiee7pw7+fkll1NzWN81FlM1Xd+EV9PyA39T5PoMBzClR2UfziJtGX/b49DuCf+V139b++nObthH4fxn1s8Ll+bPBPwJDFH6MlUd08v0DUwPNzXOfZc942Rdt8MQz0jzHqMO9fMb6W53fw8D/Gy/we+I2lfbHRPyYtWzuJmvH5crOl34hyH9tz8GcwDPtjsMov8uo/dvQYfZ7N2Qe8qHbzzq/Gz5hL+M/3lo6v2vpMhv/JMX22nS+0syhuWzezgVbAxyc6z5rZmD8+/Y7OcfIvWdV/y4aA/4KpfMXkm2hvDMX1gP8Hvb8BQXXlfnEW7M/17T6Efr5Hiy+UxF/SyFcgwMePn3HgxfIv7PlrmG9vG4aRX//16xxssrqpWvfu0TP2D4/Iqr6agn6NkuRj9jEzwqgG6tsbULVZDTSh/1j6zQg7S+I9QGdTtr3xtyHXaeuZpK6/ir03Nj/8AKw6O0psJ/HnMJumdubVj4kfAHYOj19E+9H4THvjfc8CP33MPn365Nh1+DH7L8LjnfrGTXkMfPiYPQOfnpt3sxK/SAqoK4P/BDwDqt2EN9ZvpoIo8R9E7ru3Vm1sjsaNhH4duIWcx8L8tvBxOp+RlcerF1WzjHk1Pla+Pcg3qyq/bpNZs3YNiLoiAz/OqQ+Yk+ys4stPr7r7TcoCgdXUVj7A+J1S1H+ite/KBv8nuituC4vWmTNM+Gal/pKQgS9TReUH0fCg8m9UftZFVZ6ld6N8JTTs6uI3wFdzP7o3M3yu/Vvd0vjeT3/lMF7Vr7645s7OZj+4Ab/R+Q+ANGdIwJ6t+zVLfvsg/iCR3hkB+hwGXjHmQqSZPel3oL4znz5g6dmJZ6++xbmXld8G/c+k+tkqbkrYPxInwM1gf2Zz35NkP4PfAT/cht5GhZ/ezSMI8OOr3dzf0fk99/z7M/a855bAj4yf5vd3/PZ8K97SRyh5SK3dc/GfyfsX8vhnsY15eBb788Q7IO1mi3Zn+d4B5QV+Li/4O8AffHe25s7/pW5nQ7zR3+PkIa+uQZL3t1f4PfDzzy+n9GJqP//8MQMA4LPQ8/Of1wqvJDdM5Ia58jzgi0Z//hn4sba7e6z/dId4NUbo3y9Pv0JRNttNDX1x7PfN0Hy6qxO9Qd7K99cg/g0hfwDWdh25j3TxuejOs9/dwX9btnzMXvjd08p/Fuq/y/B/V8a8VTF2P7bQd68v4eM7D+27Kpy3jGZzeYlPUu7e1XlPqs+PrDnb4O+e5gNrHrmfx2zWv/5yf3pfjJ9uADfn+Yv03kzy/iboHYA3dhJg+PPlpvoOmAdKc1/+PmzS5I7xdXL7A5iXo/vlcXTQnfhtIvwDUvu2bJa9y4sa+vTGB283PeZLov6YrZLeHutbmQS4LxXMveqZwd9Ul68Qm8dd8AOwybznJn+eP4BVOxvRi9W/iTtfl6eP0Dx7/ovf/2lk/qosfFAjn6nf5OEf5/Khna/B/jCnm0cNMdsM8I8Hmh1BX6voK9hvez/wt78B/7NR2P/5mP2TeY12gHtLeG/43oBuPj+na38uJ+b1DyHnqHGLGcHNTV+d/bsKld+W0zeP+JaLAmyU2Zkb2cnsrK/LvpQOLzCfZ76qDj4+zSbx7maQ725F7xuA/8iis7dbfhUFI/Bizd+Rmf+glL8bxr2ed/2s/tw9uHdTPjxpM9xrlH166bn4s9PUt87CjF74VRP5r2+v7Zz57eteC3PrDPneo2r/9Da7fbrZiAdE2f0q4OVue1PIPPJi88BsMvewTN06HrcMOMPNd43ZoJ7me8dXzZ/vZXsvKb6bMfotzjPryi/b2V+9R/flZT537nflm2QvzaObVG5it95dvtlW896/eWie3C5Kc5IK3821ge29Aw5V1MwZm0tyZ/4/5/w7m7nirP2q8+9avd+cbg8Ojs3UPFYLq8cfDZHwET9LNiJK4AQr7jYAsdntdkLICAvCjfcbkc5Xi/WpzQqXuy4FgbsKhCbJaBHxrQBiR0RXNNFa6iWKUD5l7AxMg6/ueUYVIVXSbPhQgnzFd71AXAWKZsv1ZsEcSZ/1emyrcUaxJuhV0MF7g8fDWNuznWXAvcSswL1BcnoeRuzaX2NLcIW11bA5HX0Fojerg7Cp15cdpUX0bg8t9Milh2G9FFZLGMJOQbCnHVqQdmGM9Zvah7cV7eAqYviZtcnJ9WDuh4N7EJb0xhAMvQrq9Wp72ZsMOxwsTjoVSmoLQqbvtrisVWJ7ZFBXRo+Wti7hQyyuHGzfyNQuAtdjZVbHtmfOixN6URVt74AcKV2qhqfdQ0q2Fnz2nUrF2y3mlMrQFAtBk82JXu+gVbWRHUwMuuNlL0T1sIU9R3DOh2B9FQUs7fVQp+hLikB7e2dS8OC5CgsquF9AzcFaI9DqMNKSQRLU0aEqNjhXmjpVHd+THHPhJpsWKlszMPqwxisyiEVvSSiOijDB1NA7dcoOMbjKLMXFwSrTHcO4IjioxtoZs3dHNJePOLGm9kPbnVfIZa2doGZsI8laBHzoHJSDn550bR8z2Pmiekiz7VEct1fRUUf4bZyaw4YfOcsHIUd3N3zL96VwcMRFzO8UZ7lqw83GFiNMKTSEBq/RsWeL3X7Nl0KOFrjXdyeW0opLxp3D9arfiQcGF9twl4J25UcpGJDRabNJ2FHn8IWB0CRvnRbcasJBerPGvY616USTFubobbrEN4hF0lUnN+ME+UhQuM36rL1xtdlcRgTtEGUtD3TV9PTaNLwB0TtThGJodRKMcM8cReayO0+ahSiqNHBoFhmrLdhYtr2sE2axxtRSdW2Y5PWAvlxJrJpUbLvobWu8tAeNBAWUtOpjBTGskSxd11nbpSQNquf5Au2u4xyhRhyNNKcgqyuLEtZ50bY+qTS1sTx0MHUAiYYIZIFxluTJ7MiU5KhrH5RLFC7GFUQfLhpeBkvVcikz65yChRW83G3WIcTBfA9XqT54XTGiLqRvWngXbrauzh66lhjS4ISCgeGDdJJKZuq1vX/cQB7cWRv0opz2w26S80OQX/SJ0ZujcQClvq61Biy4HKrXHQ9BqcjySgVDaL9aqWq65VGyUmBiSFSWD007tkhOlvYNGbcMQYHrptjO8CieU2cohzuCx6hd57gBvxRiOxs7ZL+ceGYKSW1lnSb3kFldXxEUtlI50yUpp80Q90xmkESCAQfJGZWMaBhfz2C8Chz0HGwqE7VMkD/mIIg6PKohRzwYbP9EtbWJeDSpMjZDLKp9iYnkOQgrOV5lfNjKl12PB/xl16TLiSnUWoZk5ELOpVCwH+wjtLQYiqKFnK9Yyhp8ymwIZhuSFatnIMJeDn2YbHY9SK3aE79pgguvQI5LtxJ8UHNuTJVWbeARtpeL4wLvHSQuEy1E1I21hvklJlXr0jxs/RBpYoI74xvrKDHMKpAxGJdJfgVRKGhyHJpTNFma1ITuG7ejKQU6lGe75aGeideedB1AItXS9RnLrRq24EmNqSNJoGXlH2SvxJZ24RWElS0GRYYi5QxdJo1PfZYx+4EwVtCAXaitR7XtqdtJpJ9wDI9iq2DZbQmZtNWJVat9e4LPA35yjnRp5+cJDjC3lyULIkIrWcGXVLYuV4qFGJQY6DbreSqcMjABV0wFSkWnVAVBjfHouwK0mj+6ZRV6U1xRwzEmylqmNhkcYRxPwxGTH3d1T8sGBC02gY9ONqnjJx7CYvgkebBOSTmSyV6M2zvawBB1ySO1vT1GA0nTh2hbUFzrWnE/VsNlCTu03lrpYDCowZS2WzAZyJ3thoMcxycTO2WMhQcpDQQlaYfCJ3ZpJOCw3xstX64HkOfTfLR8bE4pUhdYutOSiq3GSu57UGBxztJc7dTTRWNBc5F5U0jwqKqeaXCRMzF/tFsUh3ZWZnYHu/fYHWmiJRwQ4dINyXIXlittZJCUvYrJwcev3VHcu73vd6kBcl2yr/AE6o5QoktDAmWmgyCB5KmDJBuxGfDEVcSM40oqT9JiQYJzYMPPPhaFeD1A7OSfLDLb5FkoOn2s1EdhB+P6WsFQFFxbBUyim5B1LOZoMsnY93TH9PaKQ8GiHUK4oU4Z17VRv5W02L+Ml6EWTKw0yA5DXH1dQya0Id1Ny8RMsvDWRzvXoHWMLSjq0KGDg01BO/JQaqKYgga+Skwm1FwTcmqRrqL6LqikBnehLpzTp6VDDkqAFyNbBNNpc4x9esFrdrvL4mkRYDsfBjPVjINsIjTC45GG2GsbdZv6dmRwHjJkOnVZyAIJLVlJLY+KtxDFRAoj+8gsBc8frtJYlwbWYxiaJvvxwIZyDerXJSNWAnTC2NmrbDRoStdbkUq8doRDncodrXjkkvHGCt8gi0E3isRMpjq6nLjFAk+NEQaXqKH5VpYfSxO8NJo6REobrxbbgfQnfkCYJGnkQUEbRttbXLcxO3SHYEYpOo3baGy1GERVOl3zvDw7Tr+Y/OMw0IdTUi3StiQLR5sQDcOFYCLik+cd2m7qZWMSUBxZ6A2p1CxeFKQtImnkUPvj+nIpcd1wKbdp6DmbLuq1Lc4bpLIh1JQ1JC8QfbaeIc2uNa2lE8b4JGcfI3AsxzmnexmmRxDFX7mKP9fF+nyiHIrzLTUfupFhNTb02nbJIvisfbFCmh0D2ydbYIRO8y6tZiYuuKttUS350ymHr0c4nFTJWvV6ceRocykFoYIrFyqYLwR5JDhZtgMJBHUSelA1OSn5fFzXtSMKRsZvpai+CnGaCsQGTZcbwwoIx1kGxnVJwqWO7VPZ3ZpF7COCk6NC6pSGHxaKmdXiFIqDMdaRAi7TPts28lbp9d2yaqnIZhyBL5ZqCirLLUqlS7U4+dqWd7Z7DuXXHnS1in6uQxp7GfQFe8ayYW0noVBzl4a3MlqTlnRtnnlrvIqTB/GTNkzlTuGjITaug9GuBfIsjxozp4tgt5VOiNuyncoGaiGfQdyoBW/CO2pg1yqc5ZAHcnsb2lHldbddlXV5CW3rYLBnqbx4SAmHuOhl69ZrrI1UpZkR1hqqrpJUP+wUiOAUsyZVV0EI4qJfNkR9Pp/sbsqNzo/IUk/2isGR+PnkrA6uS+zpzCkiLNa501mClTlEu6B3EWPOIlHLQLaqB9ml4kJSorGuHuGQvJVrR8iyI5tU8xGLddMZTbYnHdwzQWJf1CTbe0zZmgYDx6dmK9glupS7QysHoTTXRFewQZHa8Kc0O5toXe0uGNq7TlGjyPVAlWtBLhrnSFy2a1m2Uh+NAoNtlEXXLzaDjapSOY6NKdblImV0bw+ur4FoDKdpQ0X9ZavbIlWn7Ga/X1O6fBAxOJdzXzPGki0OAYMdOQTJQok5LMVCCopzpeaI41Rm5DmU49kLmVJgoUW5IPKRQUe2mOhQRxTc1ORx5UHOmoEVYVLw7fKMJ7A8kJt+uVvpYBfIlKvN8Y48hCnLihWRDW51IugMtYmCqBdY7rAX05ZXHXeiUtZYQIRylE9E1pLdHDOTOU3hMLdn0GJ3nBPg3orrtWTvr93u3HoByYrauUrKUd2aE3VeOfuD1oHIbjwgoOlElx5BJkVPWlwBL6p+kDZFNIYbcSVq4Hl/3hLbwr7CW09IStnMD+LOPu6MbdwS9GXqS92jEEnrFCWmobzZ1TntHuf4gJuxECpwqhv5aCzCAJkOh+W1yLkuJgPflFnXsHSjtyyhOPG7ojSms+aVcpEis4bL8SBPpTh4QrRB7XUippavaMgZ2Ue+HqQ2ft5C3NYQcWmPT4Mc1elCnVC61FsD7HhWNavdkaHc4eTFht73hTcUeypduXEsmuQmWPdIE6LQoXAzwSdSmSWX/Bkh0rSK90NCdd4ox3XMCKDf6+q4uyyrbrueT5ogr0NsoaphBpLfaAwpH7ommcNLqxpZfSVtR3RUhZAVLj6JxbGmRE6cKoY793khy+cQ5zdaPHggel6ibNVApkJzTmZ4uBOukdJsJ3xObItUSq+tfwi4UY853N6n3hkpeyeGZEzryii3o7BlrhrubAgNXWFHqKavo8xkkKpc8qtyPFjFnhBOtLAcnVU59PAmkbBA2omkZsdsdl4qKbcQOwWmFWS5qnDpPFFsrFJLes8nVld1RzreTGjLiANBHUTJcE/zVU1RFXjny0viWi5tM7V1stlAyaAceTprdhtVMW0uUsTqao6It0bX5NEfpn1BR6uJS6sVGxgl5qgy1YOun/Fami8kKTEObrNo8XqilIo6mER2BckztxbU3XWMWXvcNpuzSHZF6e9cn71mBE/voraNXHAiUN8mT7uz049HNW+u8jotDkRdKudjISI7ZJOFwYQ1ZXqlxAtucSOHda5mTkV3UWXn5Fphi7ICTfFZTAr+VLmkX/Sc4Hgn6uKYKirp1sjBKL3crgfIbNZk06n8FoJc3XdDQ7oasd/v9OaM+Z6E9xgrz4aAcgge9/wRvjq6OKZNHSuGgBegqkmXsrV0wSUb5+xvdk2QVieq3icNp4tbyi1wyif2hyXGRJYCtmdY7K4YyF/a2DudYbuuQMV069LzTvC1dtR462DuZudqAVwet8VOiLB0qA9ClW+XoJ5pQqi3ZNMohkK3Wmax3VY869scSedHAQNZXdP50kCtDpbhxG/9cdwTUuW7FbK6+MTgW5PmaOMKJK+lySBmP86JtDHc46hsrWbciiabWO3O7BzkfLaQA7oqFy3ZdxNFQIeUJMgoQK32pNWr1ervf39693T71vOlZ3drAT6/djghSN8KkvQ+vf3Iqg5tZInPS0jXhxdEMNdMqO9SxILwfBJzlxRC+PASxQkPQRw/QLyF5/iEu0QWJIm4Puo7sD0nctt56UzlnX/reM5M//l0+4L+w70/9eENxya36+aD99KHu7cP678jwP03SH+Hl0/vfofOzbPOr5oPz/94tLz+NS90o1ly+P3iTlTkdXTrlL/2K+ukvfx277cdjzOr9Jd7T3hoXhc39uXlR1Mzk/rRK5yBZ+hf/z8ntHqk1CYAAA== -->
